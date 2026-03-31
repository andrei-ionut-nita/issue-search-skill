#!/usr/bin/env python3
"""Command-line interface for the Issue Search Skill."""

import sys
import os
import argparse
import json
from pathlib import Path
from datetime import datetime

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from schema import (
    Issue,
    IssueSource,
    Postmortem,
    PostmortemTimeline,
    QAEntry,
    Environment,
    Symptom,
)
from utils import (
    get_knowledge_base_dir,
    get_date_partition,
    get_issue_file_path,
    get_postmortem_file_path,
    write_jsonl_line,
    read_jsonl_file,
    read_json_file,
    write_json_file,
    list_all_dates,
    list_issues_by_date,
    list_postmortems_by_date,
    format_iso_datetime,
    truncate_text,
)
from indexer import Indexer
from retriever import Retriever


class CLI:
    """Command-line interface."""

    def __init__(self):
        self.kb_dir = get_knowledge_base_dir()
        self.indexer = Indexer(self.kb_dir)
        self.retriever = Retriever(self.kb_dir)

    def capture_issue(self, args) -> bool:
        """Capture a new issue."""
        # Parse symptoms
        symptoms = [s.strip() for s in args.symptoms.split(",") if s.strip()] if args.symptoms else []

        # Validate symptoms
        invalid = [s for s in symptoms if not Symptom.is_valid(s)]
        if invalid:
            print(f"Error: invalid symptoms: {', '.join(invalid)}")
            print(f"Valid symptoms: {', '.join(Symptom.all_symptoms())}")
            return False

        # Create issue
        environment = Environment(
            backend=args.backend,
            frontend=args.frontend,
            infra=args.infra,
            language=args.language,
            os=args.os,
        )

        issue = Issue(
            source=args.source,
            description=args.description,
            symptoms=symptoms,
            environment=environment,
            raw_context=json.loads(args.raw_context) if args.raw_context else {},
        )

        # Validate
        errors = issue.validate()
        if errors:
            print(f"Error: {', '.join(errors)}")
            return False

        # Persist issue
        partition = get_date_partition()
        issue_file = get_issue_file_path(self.kb_dir, issue.id, partition)
        try:
            write_jsonl_line(issue_file, issue.to_json())
            print(f"✓ Captured issue {issue.id}")
            print(f"  Description: {truncate_text(issue.description, 80)}")
            print(f"  Symptoms: {', '.join(issue.symptoms)}")

            # Link to symptom index
            self.indexer.link_issue_to_symptom_index(issue.id, issue.symptoms)

            return True
        except Exception as e:
            print(f"Error: failed to capture issue: {e}")
            return False

    def generate_postmortem(self, args) -> bool:
        """Generate a postmortem from an issue."""
        # Parse timeline
        timeline = []
        if args.timeline:
            try:
                timeline_data = json.loads(args.timeline)
                for entry in timeline_data:
                    timeline.append(PostmortemTimeline(**entry))
            except Exception as e:
                print(f"Error: invalid timeline JSON: {e}")
                return False

        # Parse symptoms
        symptoms = [s.strip() for s in args.symptoms.split(",") if s.strip()] if args.symptoms else []

        # Parse tags
        tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []

        # Create postmortem
        postmortem = Postmortem(
            id=args.issue_id,
            issue_id=args.issue_id,
            summary=args.summary,
            symptoms=symptoms,
            timeline=timeline,
            root_cause=args.root_cause,
            resolution=args.resolution,
            prevention=args.prevention,
            impact=args.impact or "",
            tags=tags,
        )

        # Validate
        errors = postmortem.validate()
        if errors:
            print(f"Error: {', '.join(errors)}")
            return False

        # Persist postmortem
        partition = get_date_partition()
        postmortem_file = get_postmortem_file_path(self.kb_dir, args.issue_id, partition)
        try:
            write_json_file(postmortem_file, json.loads(postmortem.to_json()))
            print(f"✓ Generated postmortem {postmortem.id}")

            # Generate and index Q&A entry
            qa_entry = self.indexer.generate_qa_from_postmortem(postmortem)
            self.indexer.add_qa_entry(qa_entry)
            print(f"✓ Generated Q&A entry {qa_entry.id}")
            print(f"  Q: {qa_entry.question}")

            return True
        except Exception as e:
            print(f"Error: failed to generate postmortem: {e}")
            return False

    def search_solutions(self, args) -> bool:
        """Search for solutions by symptom."""
        symptoms = [s.strip() for s in args.symptom.split(",") if s.strip()]

        # Validate symptoms
        invalid = [s for s in symptoms if not Symptom.is_valid(s)]
        if invalid:
            print(f"Warning: invalid symptoms ignored: {', '.join(invalid)}")
            symptoms = [s for s in symptoms if Symptom.is_valid(s)]

        if not symptoms:
            print("Error: no valid symptoms provided")
            return False

        print(f"Searching for solutions: {', '.join(symptoms)}\n")

        results = self.retriever.search_by_symptoms(symptoms, limit=args.limit)
        self.retriever.print_results(results)

        return True

    def list_issues(self, args) -> bool:
        """List recent issues."""
        dates = list_all_dates(self.kb_dir)
        if not dates:
            print("No issues found.")
            return True

        # Iterate from most recent
        issue_count = 0
        for partition in reversed(dates):
            issue_files = list_issues_by_date(self.kb_dir, partition)
            for issue_file in reversed(issue_files):
                issue_path = self.kb_dir / "issues" / partition / issue_file
                lines = read_jsonl_file(issue_path)
                for line in lines:
                    try:
                        issue = Issue.from_json(line)
                        issue_count += 1

                        print(f"{issue_count}. [{issue.source.upper()}] {issue.id}")
                        print(f"   {truncate_text(issue.description, 100)}")
                        if issue.symptoms:
                            print(f"   Symptoms: {', '.join(issue.symptoms)}")
                        print(f"   {format_iso_datetime(issue.timestamp)}")
                        print()

                        if issue_count >= args.limit:
                            return True
                    except Exception as e:
                        print(f"Warning: failed to parse issue: {e}")

        return True

    def show_issue(self, args) -> bool:
        """Show details of a specific issue."""
        dates = list_all_dates(self.kb_dir)

        for partition in reversed(dates):
            issue_files = list_issues_by_date(self.kb_dir, partition)
            for issue_file in issue_files:
                issue_path = self.kb_dir / "issues" / partition / issue_file
                lines = read_jsonl_file(issue_path)
                for line in lines:
                    try:
                        issue = Issue.from_json(line)
                        if issue.id == args.issue_id:
                            print(f"Issue: {issue.id}")
                            print(f"Source: {issue.source}")
                            print(f"Timestamp: {format_iso_datetime(issue.timestamp)}")
                            print(f"Description: {issue.description}")
                            if issue.symptoms:
                                print(f"Symptoms: {', '.join(issue.symptoms)}")
                            if issue.environment.to_dict():
                                print(f"Environment: {json.dumps(issue.environment.to_dict(), indent=2)}")
                            if issue.raw_context:
                                print(f"Context: {json.dumps(issue.raw_context, indent=2)}")
                            return True
                    except Exception as e:
                        print(f"Warning: failed to parse issue: {e}")

        print(f"Issue {args.issue_id} not found.")
        return False

    def show_postmortem(self, args) -> bool:
        """Show details of a specific postmortem."""
        dates = list_all_dates(self.kb_dir)

        for partition in reversed(dates):
            postmortem_files = list_postmortems_by_date(self.kb_dir, partition)
            for postmortem_file in postmortem_files:
                postmortem_path = self.kb_dir / "postmortems" / partition / postmortem_file
                try:
                    data = read_json_file(postmortem_path)
                    if data and data.get("id") == args.issue_id:
                        postmortem = Postmortem.from_json(json.dumps(data))
                        print(json.dumps(json.loads(postmortem.to_json()), indent=2))
                        return True
                except Exception as e:
                    print(f"Warning: failed to parse postmortem: {e}")

        print(f"Postmortem {args.issue_id} not found.")
        return False

    def show_stats(self, args) -> bool:
        """Show statistics about the knowledge base."""
        issue_count = 0
        postmortem_count = 0
        qa_count = 0

        dates = list_all_dates(self.kb_dir)

        for partition in dates:
            issue_files = list_issues_by_date(self.kb_dir, partition)
            for issue_file in issue_files:
                issue_path = self.kb_dir / "issues" / partition / issue_file
                lines = read_jsonl_file(issue_path)
                issue_count += len(lines)

            postmortem_files = list_postmortems_by_date(self.kb_dir, partition)
            postmortem_count += len(postmortem_files)

        qa_file = self.kb_dir / "qa" / "qa_index.jsonl"
        qa_lines = read_jsonl_file(qa_file)
        qa_count = len(qa_lines)

        print(f"Knowledge Base Statistics")
        print(f"=" * 40)
        print(f"Issues captured: {issue_count}")
        print(f"Postmortems generated: {postmortem_count}")
        print(f"Q&A entries: {qa_count}")
        print(f"Date partitions: {len(dates)}")

        return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Issue Search Skill - local-first issue tracking and solution retrieval"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Capture issue
    capture_parser = subparsers.add_parser("capture", help="Capture a new issue")
    capture_parser.add_argument("--source", default="user", choices=["user", "system"], help="Issue source")
    capture_parser.add_argument("--description", required=True, help="Issue description")
    capture_parser.add_argument(
        "--symptoms",
        help="Comma-separated list of symptoms (e.g., timeout,latency_high)"
    )
    capture_parser.add_argument("--backend", help="Backend language/framework (e.g., python, go)")
    capture_parser.add_argument("--frontend", help="Frontend framework (e.g., react, vue)")
    capture_parser.add_argument("--infra", help="Infrastructure (e.g., kubernetes, docker)")
    capture_parser.add_argument("--language", help="Programming language")
    capture_parser.add_argument("--os", help="Operating system")
    capture_parser.add_argument("--raw-context", help="Raw context as JSON")

    # Generate postmortem
    postmortem_parser = subparsers.add_parser("postmortem", help="Generate a postmortem from an issue")
    postmortem_parser.add_argument("--issue-id", required=True, help="Issue ID")
    postmortem_parser.add_argument("--summary", required=True, help="Postmortem summary")
    postmortem_parser.add_argument("--symptoms", help="Comma-separated symptoms")
    postmortem_parser.add_argument("--timeline", help="Timeline as JSON array")
    postmortem_parser.add_argument("--root-cause", required=True, help="Root cause (specific and technical)")
    postmortem_parser.add_argument("--resolution", required=True, help="Resolution (what fixed it)")
    postmortem_parser.add_argument("--prevention", required=True, help="Prevention (how to avoid recurrence)")
    postmortem_parser.add_argument("--impact", help="Impact description")
    postmortem_parser.add_argument("--tags", help="Comma-separated tags")

    # Search solutions
    search_parser = subparsers.add_parser("search", help="Search for solutions by symptom")
    search_parser.add_argument("--symptom", required=True, help="Symptom(s) to search for (comma-separated)")
    search_parser.add_argument("--limit", type=int, default=5, help="Maximum results to return")

    # List issues
    list_parser = subparsers.add_parser("list", help="List recent issues")
    list_parser.add_argument("--limit", type=int, default=10, help="Maximum issues to show")

    # Show issue
    show_issue_parser = subparsers.add_parser("show-issue", help="Show issue details")
    show_issue_parser.add_argument("issue_id", help="Issue ID")

    # Show postmortem
    show_pm_parser = subparsers.add_parser("show-postmortem", help="Show postmortem details")
    show_pm_parser.add_argument("issue_id", help="Issue ID")

    # Stats
    stats_parser = subparsers.add_parser("stats", help="Show knowledge base statistics")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    cli = CLI()

    if args.command == "capture":
        success = cli.capture_issue(args)
    elif args.command == "postmortem":
        success = cli.generate_postmortem(args)
    elif args.command == "search":
        success = cli.search_solutions(args)
    elif args.command == "list":
        success = cli.list_issues(args)
    elif args.command == "show-issue":
        success = cli.show_issue(args)
    elif args.command == "show-postmortem":
        success = cli.show_postmortem(args)
    elif args.command == "stats":
        success = cli.show_stats(args)
    else:
        parser.print_help()
        return 1

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
