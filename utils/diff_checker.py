from dataclasses import dataclass, field


@dataclass
class DiffResult:
    """Result of comparing two datasets."""
    added: list = field(default_factory=list)
    modified: list = field(default_factory=list)
    removed: list = field(default_factory=list)
    unchanged: list = field(default_factory=list)

    @property
    def has_changes(self):
        return bool(self.added or self.modified or self.removed)

    @property
    def total_records(self):
        return len(self.added) + len(self.modified) + len(self.removed) + len(self.unchanged)

    @property
    def change_percentage(self):
        if self.total_records == 0:
            return 0.0
        changed = len(self.added) + len(self.modified) + len(self.removed)
        return (changed / self.total_records) * 100


class DiffChecker:
    @staticmethod
    def compare(old_data: list, new_data: list, key_field: str) -> DiffResult:
        """Compare old and new datasets using a key field for matching.

        Args:
            old_data: Previous version of records.
            new_data: Current version of records.
            key_field: Field name used to uniquely identify records.

        Returns:
            DiffResult with categorized changes.
        """
        result = DiffResult()

        old_map = {record[key_field]: record for record in old_data if key_field in record}
        new_map = {record[key_field]: record for record in new_data if key_field in record}

        old_keys = set(old_map.keys())
        new_keys = set(new_map.keys())

        for key in new_keys - old_keys:
            result.added.append(new_map[key])

        for key in old_keys - new_keys:
            result.removed.append(old_map[key])

        for key in old_keys & new_keys:
            if old_map[key] != new_map[key]:
                result.modified.append({
                    "key": key,
                    "old": old_map[key],
                    "new": new_map[key],
                })
            else:
                result.unchanged.append(old_map[key])

        return result

    @staticmethod
    def generate_report(diff: DiffResult) -> str:
        """Generate a human-readable diff report."""
        lines = ["=== Data Diff Report ==="]
        lines.append(f"Added:     {len(diff.added)}")
        lines.append(f"Modified:  {len(diff.modified)}")
        lines.append(f"Removed:   {len(diff.removed)}")
        lines.append(f"Unchanged: {len(diff.unchanged)}")
        lines.append(f"Change %:  {diff.change_percentage:.1f}%")

        if diff.added:
            lines.append("\n--- Added ---")
            for record in diff.added[:10]:
                lines.append(f"  + {record}")

        if diff.modified:
            lines.append("\n--- Modified ---")
            for change in diff.modified[:10]:
                lines.append(f"  ~ {change['key']}")

        if diff.removed:
            lines.append("\n--- Removed ---")
            for record in diff.removed[:10]:
                lines.append(f"  - {record}")

        return "\n".join(lines)
