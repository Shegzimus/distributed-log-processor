"""
Log Analyzer - Processes and analyzes generated logs to extract insights.
"""
import json
import re
from collections import defaultdict, deque
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union

class LogAnalyzer:
    def __init__(self, log_file: str):
        """Initialize the log analyzer with a log file path."""
        self.log_file = Path(log_file)
        self.log_format = self._detect_log_format()
        self.logs: List[Dict[str, Any]] = []
        self._parse_logs()
        
    def _detect_log_format(self) -> str:
        """Detect the format of the log file based on its extension."""
        ext: str = self.log_file.suffix.lower()
        if ext == '.json':
            return 'json'
        elif ext == '.csv':
            return 'csv'
        return 'txt'  # Default to text format
    
    def _parse_json_log(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a single line of JSON log."""
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            return None
    
    def _parse_text_log(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a single line of text log."""
        # Example format: 2025-07-27T21:30:00.123456 [INFO] [SERVICE-ID] [service-name]: message
        pattern: str = r'^(\S+) \[(\w+)\] \[([^\]]+)\] \[([^\]]+)\]: (.+)$'
        match: Optional[Match[str]] = re.match(pattern, line)
        if not match:
            return None
            
        timestamp, level, log_id, service, message = match.groups()
        return {
            'timestamp': timestamp,
            'level': level,
            'id': log_id,
            'service': service,
            'message': message.strip()
        }
    
    def _parse_csv_log(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a single line of CSV log."""
        # Remove surrounding quotes and parse as text log
        if line.startswith('"') and line.endswith('"'):
            return self._parse_text_log(line[1:-1])
        return None
    
    def _parse_logs(self) -> None:
        """Parse all logs in the file based on detected format."""
        if not self.log_file.exists():
            raise FileNotFoundError(f"Log file not found: {self.log_file}")
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                log_entry = None
                if self.log_format == 'json':
                    log_entry = self._parse_json_log(line)
                elif self.log_format == 'csv':
                    log_entry = self._parse_csv_log(line)
                else:  # txt format
                    log_entry = self._parse_text_log(line)
                
                if log_entry:
                    self.logs.append(log_entry)
    
    def get_log_count_by_type(self) -> Dict[str, int]:
        """Count logs by log level (INFO, WARNING, ERROR, DEBUG)."""
        counts: Dict[str, int] = defaultdict(int)
        for log in self.logs:
            counts[log.get('level', 'UNKNOWN')] += 1
        return dict(counts)
    
    def get_average_duration_by_service(self) -> Dict[str, float]:
        """Calculate average duration of operations by service (simplified example)."""
        service_times: Dict[str, List[float]] = defaultdict(list)
        
        # This is a simplified example - in a real system, you'd parse actual durations from logs
        for log in self.logs:
            if 'duration' in log:
                service_times[log.get('service', 'unknown')].append(log['duration'])
            
        return {
            service: sum(times) / len(times)
            for service, times in service_times.items()
            if times
        }
    
    def detect_error_sequences(self, window_size: int = 5) -> List[Dict[str, Any]]:
        """Detect sequences of errors that might indicate a problem."""
        error_sequences: List[Dict[str, Any]] = []
        current_sequence: List[Dict[str, Any]] = []
        
        for log in self.logs:
            if log.get('level') == 'ERROR':
                current_sequence.append(log)
                if len(current_sequence) >= window_size:
                    error_sequences.append({
                        'start_time': current_sequence[0]['timestamp'],
                        'end_time': current_sequence[-1]['timestamp'],
                        'count': len(current_sequence),
                        'service': current_sequence[0].get('service', 'unknown'),
                        'sample_messages': [log['message'] for log in current_sequence[:3]]  # First 3 messages
                    })
                    current_sequence = []
            else:
                current_sequence = []
                
        return error_sequences
    
    def detect_unusual_patterns(self) -> List[Dict[str, Any]]:
        """Detect unusual patterns in the logs."""
        unusual: List[Dict[str, Any]] = []
        
        # Example: Look for repeated error messages
        error_messages: Dict[str, int] = defaultdict(int)
        for log in self.logs:
            if log.get('level') == 'ERROR':
                error_messages[log.get('message')] += 1
        
        # Consider any error that occurs more than 5 times as unusual
        for msg, count in error_messages.items():
            if count > 5:
                unusual.append({
                    'type': 'repeated_error',
                    'message': msg,
                    'count': count,
                    'severity': 'high' if count > 10 else 'medium'
                })
                
        return unusual
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive report of log analysis."""
        return {
            'summary': {
                'total_logs': len(self.logs),
                'log_levels': self.get_log_count_by_type(),
                'unique_services': len({log.get('service') for log in self.logs if 'service' in log})
            },
            'error_analysis': {
                'error_sequences': self.detect_error_sequences(),
                'unusual_patterns': self.detect_unusual_patterns()
            },
            'service_metrics': {
                'average_durations': self.get_average_duration_by_service()
            }
        }


def main():
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python log_analyzer.py <log_file>")
        sys.exit(1)
    
    try:
        analyzer = LogAnalyzer(sys.argv[1])
        report = analyzer.generate_report()
        
        # Print a human-readable summary
        print("\n=== Log Analysis Report ===")
        print(f"Total logs analyzed: {report['summary']['total_logs']}")
        
        print("\nLog Levels:")
        for level, count in report['summary']['log_levels'].items():
            print(f"  - {level}: {count}")
            
        print("\nError Analysis:")
        if report['error_analysis']['error_sequences']:
            print("  Detected error sequences:")
            for seq in report['error_analysis']['error_sequences']:
                print(f"    - Service: {seq['service']}, Count: {seq['count']}, "
                      f"From: {seq['start_time']} to {seq['end_time']}")
        
        if report['error_analysis']['unusual_patterns']:
            print("\n  Unusual patterns detected:")
            for pattern in report['error_analysis']['unusual_patterns']:
                print(f"    - {pattern['type'].replace('_', ' ').title()}: "
                      f"{pattern['message'][:100]}... (count: {pattern['count']}, "
                      f"severity: {pattern['severity']})")
        
        print("\nAnalysis complete!")
        
    except Exception as e:
        print(f"Error analyzing logs: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
