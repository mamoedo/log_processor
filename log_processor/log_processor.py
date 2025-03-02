import argparse
import json
import sys
from collections import Counter
from pathlib import Path

DEFAULT_OUTPUT_FORMAT = 'json'

class LogProcessorException(Exception):
    """
    Base class for LogProcessor exceptions.
    """
    pass

class NoEntriesFoundError(LogProcessorException):
    """
    Raised when no log entries are found.
    """
    pass

class NoTimeElapsedError(LogProcessorException):
    """
    Raised when no time elapsed between the earliest and latest log entries.
    """
    pass

class ArgParser:
    """
    Argument parser for the cli of the script.
    """
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Process log files and generate output in JSON format.')

        # Required arguments
        self.parser.add_argument('input', nargs='+', help='Path to one or more input files.')
        self.parser.add_argument('output', help='Path to a file to save output in plain text JSON format.')

        # Optional arguments
        self.parser.add_argument('--mfip', action='store_true', help='Most frequent IP.')
        self.parser.add_argument('--lfip', action='store_true', help='Least frequent IP.')
        self.parser.add_argument('--eps', action='store_true', help='Events per second.')
        self.parser.add_argument('--bytes', action='store_true', help='Total amount of bytes exchanged.')
        self.parser.add_argument('--format', required=False, choices=['json', 'text'],
                                default='json', help='Output format (default: json)')

    def parse_args(self):
        """
        Parse input arguments and check for missing ones.
        :return: argparse.Namespace object
        """
        args = self.parser.parse_args()

        if not any([args.mfip, args.lfip, args.eps, args.bytes]):
            print('Please, run the script with at least one optional argument.')
            sys.exit(0)

        return args

class LogEntry:
    """
    Represents a single log entry from a log.
    """
    def __init__(self, timestamp, response_header_size, client_ip, http_response_code,
                 response_size, http_request_method, url, username, access_type, response_type):
        self.timestamp = timestamp
        self.response_header_size = response_header_size
        self.client_ip = client_ip
        self.http_response_code = http_response_code
        self.response_size = response_size
        self.http_request_method = http_request_method
        self.url = url
        self.username = username
        self.access_type = access_type
        self.response_type = response_type

class LogEntryParser:
    @staticmethod
    def parse_line(line):
        """
        Parses a single line of log data into a LogEntry object.
        :param line: string representing a log line
        :return: LogEntry object
        """
        fields = [value for value in line.split(' ') if value]

        if len(fields) != 10:
            print(f'Invalid log entry: {fields}')
            return

        log_entry = LogEntry(
            timestamp=float(fields[0]),
            response_header_size=int(fields[1]),
            client_ip=fields[2],
            http_response_code=fields[3],
            response_size=int(fields[4]),
            http_request_method=fields[5],
            url=fields[6],
            username=fields[7],
            access_type=fields[8],
            response_type=fields[9],
        )

        return log_entry

class LogProcessor:
    """
    Processes log files and computes statistics such as IP frequency, events per second, and total bytes exchanged.
    """
    def __init__(self, args):
        self.args = args
        self.ip_counter = Counter()
        self.earliest_timestamp = None
        self.latest_timestamp = None
        self.entries_count = 0
        self.total_bytes = 0

    def process_file(self, file_path):
        """
        Process a single log file (later can be run in a thread).
        :param file_path: Path object representing a file path
        """
        local_ip_counter = Counter()
        local_entries_count = 0
        local_total_bytes = 0
        local_earliest_timestamp = None
        local_latest_timestamp = None

        with file_path.open('r', encoding='utf-8', errors='replace') as f:
            for line in f:
                log_entry = LogEntryParser.parse_line(line)
                if log_entry:
                    local_entries_count += 1
                    if self.args.mfip or self.args.lfip:
                        local_ip_counter[log_entry.client_ip] += 1
                    if self.args.eps:
                        if local_earliest_timestamp is None or log_entry.timestamp < local_earliest_timestamp:
                            local_earliest_timestamp = log_entry.timestamp
                        if local_latest_timestamp is None or log_entry.timestamp > local_latest_timestamp:
                            local_latest_timestamp = log_entry.timestamp
                    if self.args.bytes:
                        local_total_bytes += log_entry.response_header_size + log_entry.response_size

        self.entries_count += local_entries_count
        self.total_bytes += local_total_bytes
        self.ip_counter.update(local_ip_counter)

        if self.args.eps:
            if self.earliest_timestamp is None or local_earliest_timestamp < self.earliest_timestamp:
                self.earliest_timestamp = local_earliest_timestamp
            if self.latest_timestamp is None or local_latest_timestamp > self.latest_timestamp:
                self.latest_timestamp = local_latest_timestamp

    def process_logs(self):
        """
        Process all log files.
        """
        for path_str in self.args.input:
            file_path = Path(path_str)
            if file_path.exists():
                self.process_file(file_path)
            else:
                raise FileNotFoundError(f"{file_path} does not exist.")

    def get_results(self):
        """
        Compute final results after processing all logs.
        @return: dict with results
        """
        result = {}
        if self.args.mfip:
            result['mfip'] = self.ip_counter.most_common(1)[0] if self.ip_counter else None
        if self.args.lfip:
            result['lfip'] = self.ip_counter.most_common()[-1] if self.ip_counter else None
        if self.args.eps:
            if self.entries_count == 0:
                raise NoEntriesFoundError('No log entries found')
            if not self.earliest_timestamp or not self.latest_timestamp:
                raise NoTimeElapsedError('No time elapsed between earliest and latest entries')
            result['eps'] = round(self.entries_count / (self.latest_timestamp - self.earliest_timestamp), 2)
        if self.args.bytes:
            result['bytes'] = self.total_bytes
        return result

class OutputWriter:
    def __init__(self, output_file, output_format):
        self.output_file = output_file
        self.output_format = output_format

    def write(self, data):
        """
        Writes data to output file.
        :param data: dict representing the data to be written
        :return:
        """
        with open(self.output_file, 'w') as f:
            if self.output_format == 'json':
                json.dump(data, f, indent=4)
            elif self.output_format == 'text':
                for key, value in data.items():
                    f.write(f"{key}: {value}\n")
            else:
                raise ValueError(f'Unsupported output format: {self.output_format}')

def main():
    """
    Entry point of the script.

    - Parses command-line arguments.
    - Processes log files and computes statistics.
    - Writes results to an output file in the given format.
    """
    args = ArgParser().parse_args()
    processor = LogProcessor(args)
    processor.process_logs()
    result = processor.get_results()
    writer = OutputWriter(args.output, args.format)
    writer.write(result)

if __name__ == '__main__':
    main()