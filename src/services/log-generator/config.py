"""
Configuration for the log generator service.
"""
import os

# Default configuration values
DEFAULT_CONFIG: dict = {
    "LOG_RATE": 30,  # Logs per second
    "LOG_TYPES": ["INFO", "WARNING", "ERROR", "DEBUG"],
    "LOG_DISTRIBUTION": {
        "INFO": 70,     # 70% of logs will be INFO
        "WARNING": 20,  # 20% of logs will be WARNING
        "ERROR": 5,     # 5% of logs will be ERROR
        "DEBUG": 5      # 5% of logs will be DEBUG
    },
    "LOG_FORMAT": ["txt", "json", "csv"], 
    "SERVICES": [
        "user-service", 
        "payment-service", 
        "order-service", 
        "inventory-service", 
        "shipping-service", 
        "notification-service", 
        "auth-service", 
        "recommendation-service", 
        "search-service", 
        "analytics-service"
    ],
    # Service-specific message templates
    "SERVICE_MESSAGES": {
        "auth-service": {
            "INFO": [
                "User {user_id} logged in successfully",
                "User authenticated with {provider} provider",
                "Session created for user {user_id}"
            ],
            "ERROR": [
                "Failed to authenticate user: {error}",
                "Invalid login attempt from {ip_address}",
                "Session creation failed for user {user_id}"
            ]
        },
        "user-service": {
            "INFO": [
                "User profile updated for {user_id}",
                "New user registered: {email}",
                "User preferences saved for {user_id}"
            ],
            "ERROR": [
                "Failed to update user profile: {error}",
                "User registration failed: {reason}",
                "Failed to fetch user data for {user_id}"
            ]
        },
        "default": {
            "INFO": [
                "Operation completed successfully",
                "Request processed",
                "Task finished"
            ],
            "WARNING": [
                "High resource usage detected",
                "Performance degradation in {component}",
                "Retrying failed operation"
            ],
            "ERROR": [
                "Operation failed: {error}",
                "Failed to process request",
                "Unexpected error occurred"
            ],
            "DEBUG": [
                "Processing request {request_id}",
                "Current state: {state}",
                "Received payload: {payload}"
            ]
        }
    },
    "ENABLE_BURSTS": True,
    "BURST_FREQUENCY": 5,
    "BURST_DURATION": 10,
    "BURST_MULTIPLIER": 7,
    "OUTPUT_FILE": "/logs/generated_logs.log",
    "CONSOLE_OUTPUT": True
}

# Load configuration from environment variables 
config: dict = {
    "LOG_RATE": int(os.environ.get("LOG_RATE", DEFAULT_CONFIG["LOG_RATE"])),
    "LOG_TYPES": os.environ.get("LOG_TYPES", ",".join(DEFAULT_CONFIG["LOG_TYPES"])).split(","),
    "LOG_FORMAT": os.environ.get("LOG_FORMAT", ",".join(DEFAULT_CONFIG["LOG_FORMAT"])).split(","),
    "SERVICES": os.environ.get("SERVICES", ",".join(DEFAULT_CONFIG["SERVICES"])).split(","),
    "ENABLE_BURSTS": os.environ.get("ENABLE_BURSTS", str(DEFAULT_CONFIG["ENABLE_BURSTS"]).lower() == "true"),
    "BURST_FREQUENCY": int(os.environ.get("BURST_FREQUENCY", DEFAULT_CONFIG["BURST_FREQUENCY"])),
    "BURST_DURATION": int(os.environ.get("BURST_DURATION", DEFAULT_CONFIG["BURST_DURATION"])),
    "BURST_MULTIPLIER": int(os.environ.get("BURST_MULTIPLIER", DEFAULT_CONFIG["BURST_MULTIPLIER"])),
    "OUTPUT_FILE": os.environ.get("OUTPUT_FILE", DEFAULT_CONFIG["OUTPUT_FILE"]),
    "CONSOLE_OUTPUT": os.environ.get("CONSOLE_OUTPUT", str(DEFAULT_CONFIG["CONSOLE_OUTPUT"])).lower() == "true"
}

# Set log distribution
LOG_DISTRIBUTION: dict = {}
for log_type in config["LOG_TYPES"]:
    env_key: str = f"LOG_DIST_{log_type}"
    if log_type in DEFAULT_CONFIG["LOG_DISTRIBUTION"]:
        LOG_DISTRIBUTION[log_type] = int(os.environ.get(env_key, DEFAULT_CONFIG["LOG_DISTRIBUTION"][log_type]))
    else:
        LOG_DISTRIBUTION[log_type] = int(os.environ.get(env_key, 0))

config["LOG_DISTRIBUTION"] = LOG_DISTRIBUTION