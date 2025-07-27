"""
Log generator module for creating sample logs with configurable rates and types.
"""
import os
import time
import random
from datetime import datetime

class LogGenerator:
    def __init__(self, config: dict):
        """Initialize the log generator with configuration settings."""
        self.config: dict = config
        self.ensure_log_directory()
        
    def ensure_log_directory(self) -> None:
        """Make sure the log directory exists."""
        log_dir: str = os.path.dirname(self.config["OUTPUT_FILE"])
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
    
    def _get_service_message(self, service: str, log_type: str) -> str:
        """Get a message template for the given service and log type."""
        # Try to get service-specific message first
        service_messages = self.config.get('SERVICE_MESSAGES', {})
        
        if service in service_messages and log_type in service_messages[service]:
            return random.choice(service_messages[service][log_type])
        
        # Fall back to default messages if service-specific not found
        if 'default' in service_messages and log_type in service_messages['default']:
            return random.choice(service_messages['default'][log_type])
        
        # Fall back to hardcoded defaults if nothing else is available
        default_messages = {
            "INFO": "Operation completed successfully in {service}",
            "WARNING": "Warning in {service}: Potential issue detected",
            "ERROR": "Error in {service}: Operation failed",
            "DEBUG": "Debug info from {service}: Processing data"
        }
        return default_messages.get(log_type, f"[{log_type}] Log message from {service}")
    
    def _get_context_data(self, service: str) -> dict:
        """Generate context data for message formatting based on service."""
        base_context = {
            'service': service,
            'timestamp': int(time.time()),
            'request_id': f"req-{random.randint(1000, 9999)}",
            'user_id': f"user-{random.randint(1, 1000)}",
            'ip_address': f"192.168.{random.randint(0, 255)}.{random.randint(0, 255)}"
        }
        
        # Add service-specific context
        if 'auth' in service:
            base_context.update({
                'provider': random.choice(['google', 'github', 'email', 'microsoft']),
                'session_id': f"sess-{random.getrandbits(64):016x}"
            })
        elif 'payment' in service:
            base_context.update({
                'amount': f"{random.uniform(10, 1000):.2f}",
                'currency': random.choice(['USD', 'EUR', 'GBP']),
                'transaction_id': f"txn-{random.getrandbits(64):016x}"
            })
            
        return base_context
    
    def generate_log_message(self) -> str:
        """Generate a random log message based on configuration and service."""
        # Select service and log type
        service: str = self._select_service()
        log_type: str = self._select_log_type()
        
        # Get message template and context
        message_template = self._get_service_message(service, log_type)
        context = self._get_context_data(service)
        
        # Format the message with context
        try:
            message = message_template.format(**context)
        except (KeyError, IndexError):
            # Fallback if formatting fails
            message = f"[{log_type}] {message_template} (formatting error)"
            
        # Generate a unique ID for this log entry
        log_id: str = f"{service.upper()}-{int(time.time())}-{random.randint(1000, 9999)}"
        timestamp: str = datetime.now().isoformat()
        
        # Create the full log entry with service context
        log_entry: str = f"{timestamp} [{log_type}] [{log_id}] [{service}]: {message}"
        return log_entry
    
    def _select_log_type(self) -> str:
        """Select a log type based on the configured distribution."""
        distribution: dict = self.config["LOG_DISTRIBUTION"]
        types: list = list(distribution.keys())
        weights: list = list(distribution.values())
        
        return random.choices(types, weights=weights, k=1)[0]
    
    def _select_service(self) -> str:
        """Select a service based on the configured distribution."""
        services: list = self.config["SERVICES"]
        return random.choice(services)
    
    def _select_log_format(self) -> str:
        """Select a log format based on the configured distribution."""
        formats: list = self.config["LOG_FORMAT"]
        return random.choice(formats)
    
    def _format_log_entry(self, log_entry: str, log_format: str) -> str:
        """Format the log entry according to the specified format."""
        if log_format == 'json':
            # Split the log entry into components for JSON formatting
            try:
                timestamp, rest = log_entry.split(' [', 1)
                log_level, rest = rest.split('] [', 1)
                log_id, rest = rest.split('] [', 1)
                service, message = rest.split(']: ', 1)
                
                log_data = {
                    'timestamp': timestamp,
                    'level': log_level,
                    'id': log_id,
                    'service': service,
                    'message': message.rstrip('\n')
                }
                return json.dumps(log_data) + '\n'
            except Exception as e:
                # Fallback to text if parsing fails
                return log_entry
                
        elif log_format == 'csv':
            # Simple CSV formatting - note: this may need escaping for complex messages
            return f'"{log_entry.strip()}"\n'
        # Default to text format
        return log_entry + '\n'

    def write_log(self, log_entry: str, log_format: str) -> None:
        """Write a log entry to the configured outputs in the specified format.
        
        Args:
            log_entry: The log message to write
            log_format: The format to use ('txt', 'json', or 'csv')
        """
        # Format the log entry
        formatted_entry = self._format_log_entry(log_entry, log_format)
        
        # Write to file if configured
        if self.config["OUTPUT_FILE"]:
            # Add format extension if not already present
            output_file = self.config["OUTPUT_FILE"]
            if not any(output_file.endswith(ext) for ext in ['.txt', '.json', '.csv']):
                output_file = f"{output_file}.{log_format}"
                
            with open(output_file, "a") as f:
                f.write(formatted_entry)
        
        # Write to console if configured
        if self.config["CONSOLE_OUTPUT"]:
            print(log_entry)
    
    def _should_start_burst(self, last_burst_time: float, burst_frequency: int) -> bool:
        """Determine if a burst should start based on the configured frequency."""
        if not self.config["ENABLE_BURSTS"]:
            return False
            
        time_since_last_burst = time.time() - last_burst_time
        # Using poisson distribution to make bursts more natural
        burst_probability = 1.0 / (burst_frequency * 60)  # Convert minutes to probability per second
        return (random.random() < burst_probability) or (time_since_last_burst > burst_frequency * 60)

    def run(self, duration: float | None = None) -> None:
        """Run the log generator for a specified duration or indefinitely.
        
        The generator can enter burst mode based on configuration, where it will temporarily
        increase the log generation rate by the configured multiplier.
        """
        print(f"Starting log generator with rate: {self.config['LOG_RATE']} logs/second")
        if self.config["ENABLE_BURSTS"]:
            print(f"Burst mode enabled: x{self.config['BURST_MULTIPLIER']} rate "
                  f"for {self.config['BURST_DURATION']}s every ~{self.config['BURST_FREQUENCY']} minutes")
        
        # Calculate base sleep time based on log rate
        base_sleep_time: float = 1.0 / self.config["LOG_RATE"] if self.config["LOG_RATE"] > 0 else 1.0
        sleep_time = base_sleep_time
        
        # Burst state tracking
        is_bursting = False
        burst_start_time = 0
        last_burst_time = 0
        
        start_time: float = time.time()
        count: int = 0
        log_format: str = self._select_log_format()
        
        try:
            while duration is None or time.time() - start_time < duration:
                current_time = time.time()
                
                # Check if we should start a burst
                if (not is_bursting and 
                    self._should_start_burst(last_burst_time, self.config["BURST_FREQUENCY"])):
                    is_bursting = True
                    burst_start_time = current_time
                    sleep_time = base_sleep_time / self.config["BURST_MULTIPLIER"]
                    print(f"\n Burst Mode Activated! Generating {self.config['BURST_MULTIPLIER']}x logs for {self.config['BURST_DURATION']}s")
                
                # Check if burst should end
                if is_bursting and (current_time - burst_start_time) >= self.config["BURST_DURATION"]:
                    is_bursting = False
                    sleep_time = base_sleep_time
                    last_burst_time = current_time
                    print(f"Burst Mode Deactivated. Resuming normal rate.\n")
                
                # Generate and write log
                log_entry: str = self.generate_log_message()
                self.write_log(log_entry, log_format)
                count += 1
                
                # Sleep to maintain the configured rate
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            print("\nLog generator stopped by user")
        
        print(f"Generated {count} log entries")