"""Module to compare two JSON objects."""
import json
from termcolor import colored

from src.logging_setup import setup_logger

logger = setup_logger()

class SpecificationComparer:
    """Class to compare two JSON objects."""

    def __init__(self, column_width, ignore_keys=None):
        self.column_width = column_width
        self.ignore_keys = [tuple(key.split(",")) for key in (ignore_keys if ignore_keys else [])]
        logger.debug("Ignoring keys: %s", self.ignore_keys)

    def create_header(self):
        """Create a header for the side-by-side comparison.
        
        Returns:
            str: The header for the side-by-side comparison.
        """
        header_separator = "-" * (self.column_width-1) + "+" + "-" * self.column_width
        header = header_separator + "\n"
        header += f"{'Original Specification':{self.column_width}}Generated Output\n"
        header += header_separator
        return header

    def compare_lines(self, expected_lines, found_lines):
        """Compare two lists of lines.
        
        Args:
            expected_lines (list): The expected lines.
            found_lines (list): The found lines.
        
        Returns:
            list: A list of side-by-side lines.
        """
        side_by_side_lines = [self.create_header()]
        for expected_colored, found_colored in zip(expected_lines, found_lines):
            if (expected_colored != found_colored
                and expected_colored not in ["{", "}", "[]"]
                and found_colored not in ["{", "}", "[]"]):
                e_colored = colored(found_colored, 'red')
                f_colored = colored(expected_colored, 'green')
                side_by_side_lines.append(f"{e_colored:{self.column_width}}{f_colored}")
        return side_by_side_lines

    def compare_nested(self, obj1, obj2, key_path=None):
        """Compare two nested JSON objects.
        
        Args:
            obj1 (dict): The original object.
            obj2 (dict): The generated object.
            key_path (list): The path to the current key.
        
        Returns:
            tuple: A tuple containing the differences and affected lines.
        """
        if obj1 == obj2 or (obj1 in [None, {}, []] and obj2 in [None, {}, []]):
            return [], []

        if isinstance(obj1, dict) and isinstance(obj2, dict):
            differences, affected_lines = self._compare_dicts(obj1, obj2, key_path)
            return differences, affected_lines

        return self._compare_json_strings(obj1, obj2)

    def _compare_dicts(self, obj1, obj2, key_path):
        """Compare two dictionaries.
        
        Args:
            obj1 (dict): The original dictionary.
            obj2 (dict): The generated dictionary.
            key_path (list): The path to the current key.
        
        Returns:
            tuple: A tuple containing the differences and affected lines.
        """
        differences = []
        affected_lines = []
        all_keys = set(obj1.keys()).union(obj2.keys())
        for key in all_keys:
            new_key_path = key_path + [key] if key_path else [key]
            key_diff, key_affected_lines = (
                self.compare_nested(obj1.get(key), obj2.get(key), new_key_path)
            )
            if key_diff:
                differences.append(f"Key Path: {' -> '.join(new_key_path)}")
                differences.extend(key_diff)
                affected_lines.extend(key_affected_lines)
        return differences, affected_lines

    def _compare_json_strings(self, obj1, obj2):
        """Compare two JSON strings.
        
        Args:
            obj1 (str): The original JSON string.
            obj2 (str): The generated JSON string.
        
        Returns:
            tuple: A tuple containing the differences and affected lines.
        """
        expected = json.dumps(obj2, indent=2, sort_keys=True)
        found = json.dumps(obj1, indent=2, sort_keys=True)
        expected_lines = expected.splitlines()
        found_lines = found.splitlines()

        max_lines = max(len(expected_lines), len(found_lines))
        side_by_side_lines = [self.create_header()]

        affected_lines = []
        for i in range(max_lines):
            expected_line = expected_lines[i] if i < len(expected_lines) else None
            found_line = found_lines[i] if i < len(found_lines) else None

            if (expected_line != found_line and
                expected_line not in ["{", "}", "[]"] and
                found_line not in ["{", "}", "[]"]):
                if expected_line is None:
                    e_colored = colored("MISSING", 'yellow')  # Additional in generated output
                    f_colored = colored(found_line, 'green')  # Correct in generated output
                elif found_line is None:
                    e_colored = colored(expected_line, 'red') # Missing in generated output
                    f_colored = colored("MISSING", 'yellow')  # Additional in original specification
                else:
                    e_colored = colored(expected_line, 'red') # Incorrect in original specification
                    f_colored = colored(found_line, 'green')  # Correct in generated output

                side_by_side_lines.append(f"{e_colored:{self.column_width}}{f_colored}")
                affected_lines.append(i)
        return side_by_side_lines, affected_lines

    def compare_objects(self, obj1, obj2):
        """Compare two JSON objects.
        
        Args:
            obj1 (dict): The original object.
            obj2 (dict): The generated object.
        
        Returns:
            int: The exit code.
        """
        deltas, summary_stats = self._find_differences(obj1, obj2)
        summary_table = self._format_summary_table(summary_stats)
        return self._handle_deltas(deltas, summary_table)

    def _find_differences(self, obj1, obj2):
        all_keys = self._combine_keys(obj1, obj2)
        differences, summary_stats = self._compare_and_classify(obj1, obj2, all_keys)
        return differences, summary_stats

    def _combine_keys(self, obj1, obj2):
        all_keys = set(obj1.keys()).union(obj2.keys())
        return [key for key in all_keys if not any(key in t for t in self.ignore_keys)]

    # def _compare_and_classify(self, obj1, obj2, keys):
    #     missing_lines = []
    #     additional_lines = []
    #     incorrect_lines = []
    #     deltas = []
    #     total_items = 0
    #     all_affected_lines = []

    #     for key in keys:
    #         logger.debug(f"Current key: {key}")
    #         total_items += 1
    #         key_diff, affected_lines = self.compare_nested(
    #             obj1.get(key), obj2.get(key), key_path=[key]
    #         )
    #         all_affected_lines.extend(affected_lines)
    #         if key_diff:
    #             delta = "\n".join(key_diff)
    #             deltas.append(delta)
    #             for line, line_count in zip(key_diff, affected_lines):
    #                 if "MISSING" in line:
    #                     additional_lines.extend([line_count] * line.count("MISSING"))
    #                 if colored("MISSING", 'red') in line:
    #                     missing_lines.extend([line_count] * line.count(colored("MISSING", 'red')))
    #                 if colored("MISSING", 'yellow') not in line and "MISSING" not in line:
    #                     incorrect_lines.append(line_count)

    #     summary_stats = {
    #         "missing_from_output": len(missing_lines),
    #         "additional_in_output": len(additional_lines),
    #         "incorrect_items": len(incorrect_lines),
    #         "total_items": total_items,
    #         "missing_lines": missing_lines,
    #         "additional_lines": additional_lines,
    #         "incorrect_lines": incorrect_lines,
    #         "all_affected_lines": all_affected_lines
    #     }
    #     return deltas, summary_stats
    def _compare_and_classify(self, obj1, obj2, keys):
        summary_stats = {
            "missing_lines": [],
            "additional_lines": [],
            "incorrect_lines": [],
            "deltas": [],
            "total_items": 0,
            "all_affected_lines": []
        }

        for key in keys:
            logger.debug("Current key: %s", key)
            summary_stats["total_items"] += 1
            key_diff, affected_lines = self.compare_nested(
                obj1.get(key), obj2.get(key), key_path=[key]
            )
            summary_stats["all_affected_lines"].extend(affected_lines)
            self._classify_differences(key_diff, affected_lines, summary_stats)

        summary_stats.update({
            "missing_from_output": len(summary_stats["missing_lines"]),
            "additional_in_output": len(summary_stats["additional_lines"]),
            "incorrect_items": len(summary_stats["incorrect_lines"])
        })
        return summary_stats["deltas"], summary_stats

    def _classify_differences(self, key_diff, affected_lines, summary_stats):
        if key_diff:
            delta = "\n".join(key_diff)
            summary_stats["deltas"].append(delta)
            for line, line_count in zip(key_diff, affected_lines):
                if "MISSING" in line:
                    summary_stats["additional_lines"].extend(
                        [line_count] * line.count("MISSING")
                    )
                if colored("MISSING", 'red') in line:
                    summary_stats["missing_lines"].extend(
                        [line_count] * line.count(colored("MISSING", 'red'))
                    )
                if colored("MISSING", 'yellow') not in line and "MISSING" not in line:
                    summary_stats["incorrect_lines"].append(line_count)

    def _format_summary_table(self, summary_stats):
        """Format the summary table.
        
        Args:
            summary_stats (dict): The summary statistics.
        
        Returns:
            str: The formatted summary table.
        """
        all_affected_lines = list(set(summary_stats["all_affected_lines"]))
        if not all_affected_lines:
            return ""
        all_affected_lines.sort()
        groups = [[all_affected_lines[0]]]
        for line in all_affected_lines[1:]:
            if line == groups[-1][-1] + 1:
                groups[-1].append(line)
            else:
                groups.append([line])

        def format_grouped_lines(lines):
            if not lines:
                return "N/A"

            lines.sort()
            groups = [[lines[0]]]
            for line in lines[1:]:
                if line == groups[-1][-1] + 1:
                    groups[-1].append(line)
                else:
                    groups.append([line])
            return ", ".join(
                "-".join(map(str, (g[0], g[-1]))) if len(g) > 1 else str(g[0])
                for g in groups
            )

        def format_lines(value, width):
            lines = [value[i:i+width] for i in range(0, len(value), width)]
            padding = " " * 57
            return f"\n{padding}".join(lines)

        missing_lines_str = format_lines(
            format_grouped_lines(summary_stats["missing_lines"]), 50
        )
        additional_lines_str = format_lines(
            format_grouped_lines(summary_stats["additional_lines"]), 50
        )
        incorrect_lines_str = format_lines(
            format_grouped_lines(summary_stats["incorrect_lines"]), 50
        )

        total_items = (
            summary_stats["missing_from_output"]
            + summary_stats["additional_in_output"]
            + summary_stats["incorrect_items"]
        )

        missing_percentage = (
            f"{float(summary_stats['missing_from_output']/total_items*100):<17.2f}"
        )
        additional_percentage = (
            f"{float(summary_stats['additional_in_output']/total_items*100):<17.2f}"
        )
        incorrect_percentage = (
            f"{float(summary_stats['incorrect_items']/total_items*100):<17.2f}"
        )

        summary_table = f"\n{'Category':<30}{'Count':<10}{'Percentage (%)':<17}{'Lines'}\n"
        summary_table += "-" * 70 + "\n"
        summary_table += (
            f"{'Missing from generated':<30}{int(summary_stats['missing_from_output']):<10}"
            f"{missing_percentage}{missing_lines_str}\n"
        )
        summary_table += (
            f"{'Additional in generated':<30}{int(summary_stats['additional_in_output']):<10}"
            f"{additional_percentage}{additional_lines_str}\n"
        )
        summary_table += (
            f"{'Incorrect':<30}{int(summary_stats['incorrect_items']):<10}"
            f"{incorrect_percentage}{incorrect_lines_str}\n"
        )
        summary_table += (
            f"{'' if summary_stats['total_items'] == total_items else 'Total':<30}"
            f"{summary_stats['total_items']:<10}{'100.00':<17}\n"
        )

        return summary_table

    def _handle_deltas(self, deltas, summary_table):
        """Handle the deltas.
        
        Args:
            deltas (list): A list of differences.
            summary_table (str): The summary table.
        
        Returns:
            int: The exit code.
        """
        if deltas:
            logger.info("Differences found!")
            for delta in deltas:
                logger.info(delta)
            logger.info(colored(summary_table, 'blue'))
            return 1
        logger.info(colored("No differences found. Everything is perfect!", 'green'))
        return 0
