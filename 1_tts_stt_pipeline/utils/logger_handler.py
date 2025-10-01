import sys
import os
from datetime import datetime
import configparser
from configparser import ConfigParser

class Logger:
    def __init__(self):
        """Constructor
        """
        # Read config for log path
        config = configparser.ConfigParser()
        config.read("config.ini")
        
        self.logs_directory = config.get('Paths', 'log_path')
        self.ensure_logs_directory_exists()
        self.log_file = self.generate_log_file_name()
        self.terminal = sys.stdout
        self.log = open(self.log_file, 'a')  # Open log file in append mode

    def ensure_logs_directory_exists(self):
        """Create the logs directory if it does not exist.
        """
        if not os.path.exists(self.logs_directory):
            os.makedirs(self.logs_directory)

    def generate_log_file_name(self):
        """Generates the logfile name

        Returns:
            str: Filename for logfile
        """
        base_name = datetime.now().strftime('%Y-%m-%d_%H-%M')
        log_file = os.path.join(self.logs_directory, f"logfile_{base_name}.txt")
        count = 1
        
        while os.path.exists(log_file):
            log_file = os.path.join(self.logs_directory, f"logfile_{base_name}_{count}.txt")
            count += 1
        
        return log_file

    def write(self, message):
        """Write sysout to file and console

        Args:
            message (Any): text to be written
        """
        if message.strip():
            # Get current timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_message = f"[{timestamp}] {message}\n"
            
            self.terminal.write(log_message)  
            self.log.write(log_message)
            self.log.flush()

    def flush(self):
        """Flush the terminal and log file
        """
        self.terminal.flush()
        self.log.flush()

    def close(self):
        """Close Logger Instance
        """
        self.log.close()