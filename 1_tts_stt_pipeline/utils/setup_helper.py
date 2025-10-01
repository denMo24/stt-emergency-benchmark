import configparser
from configparser import ConfigParser
import os

class SetupHelper:
    def __init__(self, iniTechnology: str, cwd: str):
        """Constructor of SetupHelper

        Args:
            iniTechnology (str): Which technology is being initialized
            cwd (str): Path to current working directory
        """
        print(f"Init SetupHelper for {iniTechnology}")
        try:
            config = configparser.ConfigParser()
            config.read("config.ini")
            
            match iniTechnology:
                case "piper": 
                    self.config_values = self.initializePiperConfig(config, cwd)
                case "audio_editing":
                    self.config_values = self.initializeAudioEditingConfig(config, cwd)
                case "tts_recapp":
                    self.config_values = self.initializeSTTRecapp(config, cwd)
                case "tts_whisper":
                    self.config_values = self.initializeSTTWhisper(config, cwd)
                case "tts_speechbrain":
                    self.config_values = self.initializeSTTSpeechBrain(config, cwd)
                case "tts_vosk":
                    self.config_values = self.initializeSTTVosk(config, cwd)
                case "metrics":
                    self.config_values = self.initializeMetrics(config, cwd)
                case _:
                    print("No config-handler found matching")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            self.config_values = None
                  
    def getConfigValues(self):
        """Fetching config values

        Returns:
            dict: config values
        """
        return self.config_values  

    def initializePiperConfig(self, conf: ConfigParser, cwd: str): 
        """Loading configs from config-file for PiperTTS

        Args:
            conf (ConfigParser): Content of config.ini file
            cwd (str): Path to current working directory

        Returns:
            dict: config values for PiperTTS
        """
        # Access values from the configuration file
        db_name = conf.get('MongoDBDatabase', 'db_name')
        db_collection = conf.get('MongoDBDatabase', 'db_collection')
        db_host = conf.get('MongoDBDatabase', 'db_host')
        db_port = conf.get('MongoDBDatabase', 'db_port')
        collection_id = conf.get('MongoDBCollection', 'collection_id')
        collection_text = conf.get('MongoDBCollection', 'collection_text')
        
        # Build Folder / Pathstructure
        script_dir = cwd
        piper_dir = os.path.join(cwd, conf.get('Paths', 'piper_path'))
        audio_dir = os.path.join(cwd, conf.get('Paths', 'piper_output_path'))
        fullFile_dir = os.path.join(cwd, conf.get('Paths', 'piper_output_fullconversations_path'))
        piper_exe = os.path.join(piper_dir, "piper.exe")
        
        # Create dictionary with values
        config_values = {
            'db_name': db_name,
            'db_collection': db_collection,
            'db_host': db_host,
            'db_port': int(db_port),
            'collection_id': collection_id,
            'collection_text': collection_text,
            'script_dir': script_dir,
            'piper_dir': piper_dir,
            'audio_dir': audio_dir,
            'fullFile_dir': fullFile_dir,
            'piper_exe': piper_exe
        }
        return config_values

    def initializeAudioEditingConfig(self, conf: ConfigParser, cwd: str):
        """Loading configs from config-file for Audio Editing

        Args:
            conf (ConfigParser): Content of config.ini file
            cwd (str): Path to current working directory

        Returns:
            dict: config values for Audio Editing
        """
        # Access values from the configuration file
        synthesized_files = conf.get('Paths', 'piper_output_fullconversations_path')
        
        # Build Folder / Pathstructure
        script_dir = cwd
        source_dir = os.path.join(cwd, synthesized_files)
        output_dir = os.path.join(cwd, conf.get('Paths', 'audio_editing_output_path'))
        ambient_dir = os.path.join(cwd, conf.get('Paths', 'ambient_source_path'))
        # Create dictionary with values
        config_values = {
            'script_dir': script_dir,
            'source_dir': source_dir,
            'output_dir': output_dir,
            'ambient_dir': ambient_dir
        }
        
        return config_values
    
    def initializeSTTRecapp (self, conf: ConfigParser, cwd: str):
        """Loading configs from config-file for Recapp

        Args:
            conf (ConfigParser): Content of config.ini file
            cwd (str): Path to current working directory

        Returns:
            dict: config values for Recapp
        """
        source_dir = os.path.join(cwd, conf.get('Paths', 'audio_editing_output_path'))
        token = conf.get('Recapp', 'token')
        api_url = conf.get('Recapp', 'url')
        model = conf.get('Recapp', 'recapp_model')
        db_host = conf.get('MongoDBDatabase', 'db_host')
        db_port = conf.get('MongoDBDatabase', 'db_port')
        recapp_db_name = conf.get('Recapp', 'recapp_db_name')
        req_collection = conf.get('Recapp', 'recapp_req_collection')
        transcript_db = conf.get('STTTranscriptions', 'transcription_db_name')
        transcript_collection = conf.get('STTTranscriptions', 'transcription_collection')
        
        # Create dictionary with values
        config_values = {
            'source_dir': source_dir,
            'model': model,
            'token': token,
            'api': api_url,
            'db_host': db_host,
            'db_port': int(db_port),
            'recapp_db_name': recapp_db_name,
            'req_collection': req_collection,
            'transcript_db': transcript_db,
            'transcript_collection': transcript_collection
        }
        return config_values
    
    def initializeSTTWhisper (self, conf: ConfigParser, cwd: str):
        """Loading configs from config-file for whisper

        Args:
            conf (ConfigParser): Content of config.ini file
            cwd (str): Path to current working directory

        Returns:
            dict: config values for whisper
        """
        source_dir = os.path.join(cwd, conf.get('Paths', 'audio_editing_output_path'))
        output_dir = os.path.join(cwd, conf.get('STTTranscriptions', 'transcription_local_whisper'))
        db_host = conf.get('MongoDBDatabase', 'db_host')
        db_port = conf.get('MongoDBDatabase', 'db_port')
        transcript_db = conf.get('STTTranscriptions', 'transcription_db_name')
        transcript_collection = conf.get('STTTranscriptions', 'transcription_collection')
        
        # Create dictionary with values
        config_values = {
            'source_dir': source_dir,
            'output_dir': output_dir,
            'db_host': db_host,
            'db_port': int(db_port),
            'transcript_db': transcript_db,
            'transcript_collection': transcript_collection
        }
        return config_values
    
    def initializeSTTSpeechBrain (self, conf: ConfigParser, cwd: str):
        source_dir = os.path.join(cwd, conf.get('Paths', 'audio_editing_output_path'))
        output_dir = os.path.join(cwd, conf.get('STTTranscriptions', 'transcription_local_speechbrain'))
        db_host = conf.get('MongoDBDatabase', 'db_host')
        db_port = conf.get('MongoDBDatabase', 'db_port')
        transcript_db = conf.get('STTTranscriptions', 'transcription_db_name')
        transcript_collection = conf.get('STTTranscriptions', 'transcription_collection')
        
        # Create dictionary with values
        config_values = {
            'source_dir': source_dir,
            'output_dir': output_dir,
            'db_host': db_host,
            'db_port': int(db_port),
            'transcript_db': transcript_db,
            'transcript_collection': transcript_collection
        }
        return config_values
    
    def initializeSTTVosk (self, conf: ConfigParser, cwd: str):
        """Loading configs from config-file for Vosk

        Args:
            conf (ConfigParser): Content of config.ini file
            cwd (str): Path to current working directory

        Returns:
            dict: config values for Vosk
        """
        source_dir = os.path.join(cwd, conf.get('Paths', 'audio_editing_output_path'))
        output_dir = os.path.join(cwd, conf.get('STTTranscriptions', 'transcription_local_vosk'))
        model_path = os.path.join(cwd, conf.get('STTTranscriptions', 'vosk_model_path'))
        db_host = conf.get('MongoDBDatabase', 'db_host')
        db_port = conf.get('MongoDBDatabase', 'db_port')
        transcript_db = conf.get('STTTranscriptions', 'transcription_db_name')
        transcript_collection = conf.get('STTTranscriptions', 'transcription_collection')
        
        # Create dictionary with values
        config_values = {
            'source_dir': source_dir,
            'output_dir': output_dir,
            'model_path': model_path,
            'db_host': db_host,
            'db_port': int(db_port),
            'transcript_db': transcript_db,
            'transcript_collection': transcript_collection
        }
        return config_values
    
    def initializeMetrics (self, conf: ConfigParser, cwd: str):
        """Loading configs from config-file to calculate metrics

        Args:
            conf (ConfigParser): Content of config.ini file
            cwd (str): Path to current working directory

        Returns:
            dict: config values to calculate metrics
        """
        # Access values from the source texts
        db_name = conf.get('MongoDBDatabase', 'db_name')
        db_collection = conf.get('MongoDBDatabase', 'db_collection')
        db_host = conf.get('MongoDBDatabase', 'db_host')
        db_port = conf.get('MongoDBDatabase', 'db_port')
        collection_id = conf.get('MongoDBCollection', 'collection_id')
        collection_text = conf.get('MongoDBCollection', 'collection_text')
        transcript_db = conf.get('STTTranscriptions', 'transcription_db_name')
        transcript_collection = conf.get('STTTranscriptions', 'transcription_collection')
        
        # Create dictionary with values
        config_values = {
            'db_name': db_name,
            'db_collection': db_collection,
            'db_host': db_host,
            'db_port': int(db_port),
            'collection_id': collection_id,
            'collection_text': collection_text,
            'transcript_db': transcript_db,
            'transcript_collection': transcript_collection
        }
        return config_values