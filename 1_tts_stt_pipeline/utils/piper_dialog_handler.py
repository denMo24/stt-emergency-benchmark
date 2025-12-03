import re
import os
from typing import List
from models.PiperTTSElement import PiperTTSElement
from models.SpeakerElement import SpeakerElement

class PiperDialogHandler:
    CONST_DIALOG_ELEMENTS = 2 #Dialog is always 'Speaker: "Spoken Text"', seperated by ":"
    CONST_MAP_NUMERICAL_REPLACER = {
        1: 'Smith',
        2: 'Connor',
        3: 'White',
        4: 'Tabula'
    }
    
    def __init__(self):
        """Constructor
        """
        pass
      
    def processTextFromMongoDB(self, textToBeProcessed):
        """Process text to not contain any unnecessary spaces or line breaks.

        Args:
            textToBeProcessed (Any): Text to be processed

        Returns:
            list[str]: A list of each line in the source text as a element in a list.
        """
        # Normalize the dialogue by replacing multiple line breaks with a single one
        normalized_text = re.sub(r'\n{2,}', '\n', textToBeProcessed).strip()
        # Split the dialogue into lines
        processed_text = normalized_text.split('\n')
        return processed_text
    
    def formatSpeaker(self, speakerName: str):
        """Return the parts of the name from a speaker

        Args:
            speakerName (str): Full Speaker identification 

        Returns:
            name: Name of the speaker
            lastName: Last name of speaker, if it exists
            fullName: Full Name of the speaker
        """
        name = lastName = fullName = ''
        parts = speakerName.split()
        
        if len(parts) > 1:  # if there are 2 parts in the speaker name
            name = parts[0]
            lastName = parts[1]  # lastname is the last element
            if lastName.isdigit():
                print("Lastname is actually a integer, replacing with name")
                tempName = lastName
                lastName = self.CONST_MAP_NUMERICAL_REPLACER[int(tempName)]
                fullName = f"{name} {lastName}"
            if name == 'Frau' or name == 'Herr':
                name = ''
                fullName = lastName
        else:
            name = speakerName
            fullName = speakerName
        return name, lastName, fullName
    
    def identifyAllSpeakers(self, speakerEle: PiperTTSElement, speaker_count: int, allIdentifiedSpeakers: List[SpeakerElement], allUnidentifiedSpeakers: List[SpeakerElement]):
        """Identifying the speaker of a given PiperTTSElement, incrementing the counter of speakers to match a voice later on.

        Args:
            speakerEle (PiperTTSElement): Spoken Dialog with Speaker and Text
            speaker_count (int): speaker identification
            allIdentifiedSpeakers (List[SpeakerElement]): List of all Identified Speakers
            allUnidentifiedSpeakers (List[SpeakerElement]): List of all Unidentified Speakers

        Returns:
            int: speaker count after identification.
        """
        name = lastName = fullName = str('')
        #Get the current Speaker from the dialog line
        speaker = speakerEle.speaker
        #Split into Name and Last name -> Bob Builder -> Bob / Builder
        name, lastName, fullName = self.formatSpeaker(speaker)
        
        # if name and lastname is not in list and both contain values        
        if (not any(name == person.name and lastName == person.lastname for person in allIdentifiedSpeakers)) and \
            (name and lastName):
            print(f"New name '{name} {lastName}' to add to names-list")
            allIdentifiedSpeakers.append(SpeakerElement(speaker_count, name, lastName, fullName))
            speaker_count += 1
        else:
            #is already in Identified Speakers
            print(f"Element { speakerEle.element_id } already identified")
            if (not any(speaker == alias_speaker.name for alias_speaker in allUnidentifiedSpeakers)) and \
            (not any(name == person.name and lastName == person.lastname for person in allIdentifiedSpeakers)):
                print(f"New Alias, add {speaker} to alias-list.")
                allUnidentifiedSpeakers.append(SpeakerElement(0, name, lastName, fullName))
        return speaker_count;        
        
    def lookForAliases (self, aliasToBeChecked: SpeakerElement, identifiedSpeakers: List[SpeakerElement], noMatchesList: List[SpeakerElement]):
        """Check if a name has a variation in the list of identified speakers (missing lastname)

        Args:
            aliasToBeChecked (SpeakerElement): SpeakerElement-Object of the speaker to be checked
            identifiedSpeakers (List[SpeakerElement]): List of all identified Speakers in the dialog.
            noMatchesList (List[SpeakerElement]): List of all speakers that could not be matched with the identified speakers.
        """
        foundMatch = False
        print(f"Checking unmapped User: {aliasToBeChecked.fullname}")
        for speaker in identifiedSpeakers:
            print(f"Comparing to Speaker: {speaker.fullname}")
            if aliasToBeChecked.name == speaker.name:
                print ("Found a match")
                foundMatch = True
                break
        if not foundMatch and (not any(aliasToBeChecked.name == noMatch.name for noMatch in noMatchesList)):
            print ("no match found, adding to nomatches found")
            noMatchesList.append(aliasToBeChecked)
                    
    def createRandomSpeakers(self, id, speaker: SpeakerElement, allSpeakers: List[SpeakerElement]):
        """If the Speaker could not be identified, a incrementing number will be added as the voice to be used in the synthesizing.

        Args:
            id (Any): Voice-ID to add
            speaker (SpeakerElement): What SpeakerElement needs to be modified
            allSpeakers (List[SpeakerElement]): List of all speakers

        Returns:
            _type_: Returning incremented ID for later use.
        """
        print(f"Adding increasing voice_id to unidentified speaker: {speaker}")
        allSpeakers.append(SpeakerElement(id, speaker.name, speaker.lastname, speaker.fullname))
        id += 1
        return id
                   
    def getDialogueParticipantsInformation(self, completeDialog: List[PiperTTSElement]):
        """Identify all Speakers in a given dialog

        Args:
            completeDialog (List[PiperTTSElement]): Full Processed Dialog

        Returns:
            len(name_list): number of Speakers in a text
            list[SpeakerElement]: Identified speakers
        """
        # temp dictionary and counter to save found names
        name_list: List[SpeakerElement] = [] #contains all Speakers
        alias_list: List[SpeakerElement] = [] 
        nomatchesfound_list: List[SpeakerElement] = []
        speaker_count = 1
        #Iterate through the whole converstation line by line
        for element in completeDialog:
            speaker_count = self.identifyAllSpeakers(element, speaker_count, name_list, alias_list)
        
        print(f"Current speakers: {len(name_list)} \n {name_list}")
        print(f"Not mapped speakers: {len(alias_list)}\n {alias_list}\nStarting to map unmapped speakers")
        print(f"speaker count after mapping all speakers: {speaker_count} (should be 1 bigger than current speakers)")
        
        for unmapped_speaker in alias_list:
            self.lookForAliases(unmapped_speaker, name_list, nomatchesfound_list)
        
        print(f"unmapped user after alias matching: {nomatchesfound_list}")
        
        for element in nomatchesfound_list:
            speaker_count = self.createRandomSpeakers(speaker_count, element, name_list)

        return len(name_list), name_list

    # Work througn 1 Conversation
    def initDialogue(self, id, dialogRawText):
        """Start to process dialog and prepare it for Text-To-Speech

        Args:
            id (_type_): _description_
            dialogRawText (_type_): _description_

        Returns:
            _type_: _description_
        """
        #Process the text before continuing
        paras = self.processTextFromMongoDB(dialogRawText)

        dialogparts_list: List[PiperTTSElement] = []

        for index, paragraph in enumerate(paras):
            #Split into Speaker and spoken text
            dialog_paragraph = paragraph.split(":")
            #Filter Descriptors with no spoken text.
            if ((len(dialog_paragraph) == self.CONST_DIALOG_ELEMENTS) and (dialog_paragraph[1] != '')):
                dialogparts_list.append(PiperTTSElement(
                    id, 
                    index, 
                    dialog_paragraph[0].strip(), 
                    dialog_paragraph[1].strip().replace('\"',''))
                )
        print(f"List with objects {dialogparts_list}")        

        numOfSpeakers, speakers = self.getDialogueParticipantsInformation(dialogparts_list)
        print (f"Identified Speakers: {numOfSpeakers}")
        print(f"Speakers: {speakers}")
        
        for element in dialogparts_list:
            self.addVoiceModelToSpeakerDialog(speakers, element)
            
        print (f"Finished list after matching voice_id:\n")
        print(dialogparts_list)
        return dialogparts_list, numOfSpeakers, speakers
    
    def voiceModelSelector(self, modelID):
        """Select a PiperTTS Voice Model to use

        Args:
            modelID (int): Model-ID

        Returns:
            str: Path to Model file
        """
        match modelID:
                case 1: 
                    return os.path.join("voices", "thorsten", "de_DE-thorsten-high.onnx")
                case 2: 
                    return os.path.join("voices", "kerstin", "de_DE-kerstin-low.onnx")
                case 3: 
                    return os.path.join("voices", "ramona", "de_DE-ramona-low.onnx")
                case 4: 
                    return os.path.join("voices", "karlsson", "de_DE-karlsson-low.onnx")
                case 5: 
                    return os.path.join("voices", "pavoque", "de_DE-pavoque-low.onnx")
                case default: 
                    return os.path.join("voices", "thorsten", "de_DE-thorsten-high.onnx")
    
    def addVoiceModelToSpeakerDialog (self, speakers: List[SpeakerElement], dialogelement: PiperTTSElement):
        """Work through list of speakers, adding their corresponding voice-model ID to their Text to mimic a authentic conversation.

        Args:
            speakers (List[SpeakerElement]): List of all Speakers
            dialogelement (PiperTTSElement): PiperTTSElement containing the dialog to be syntzesized.
        """
        print(f"Speaker to identify: {dialogelement.speaker}")
        matchFound = False
        for speaker in speakers:
            currentSpeakerToBeMatched = dialogelement.speaker
            # More than 2 elements before the text -> paramedic 1 to paramedic 2: "Text"
            name, lastName , fullName = self.formatSpeaker(currentSpeakerToBeMatched)
            # If speaker consists of only 1 element
            if (lastName == ''):
                if ((name == speaker.name)):
                    print(f"Identified {dialogelement.speaker}")
                    dialogelement.voice = speaker.speaker_num
                    matchFound = True
            else:
                if ((name == speaker.name)) and (fullName == speaker.fullname) and (lastName == speaker.lastname):
                    print(f"Identified {dialogelement.speaker}")
                    dialogelement.voice = speaker.speaker_num
                    matchFound = True
            if matchFound:
                break
        if not matchFound:
            # If after all there is a mismatch, set voice to 0 to assign random voice
            dialogelement.voice = 0