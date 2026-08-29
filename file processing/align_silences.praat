form Align silences
    sentence Input_folder ./2. First Normalization/GA/
    sentence Output_folder ./3. Trim/GA/
    positive Onset_threshold_dB 50
    positive Offset_threshold_dB 40
endform

# Create output directory if necessary
createDirectory: output_folder$

# Get all WAV files
Create Strings as file list: "wavFiles", input_folder$ + "/*.wav"
fileList = selected("Strings")
nFiles = Get number of strings

for i from 1 to nFiles

    selectObject: fileList
    fileName$ = Get string: i

    # Read sound
    sound = Read from file: input_folder$ + "/" + fileName$
    endTime = Get total duration

    # Create intensity contour. Time step is set explicity to 2ms
    To Intensity: 75, 0.002, "yes"
    intensity = selected("Intensity")

    # Find the first frame above the onset threshold and the last frame
    # above the offset threshold, i.e. the onset and offset of speech.
    # Scan forward once: onset is set only the first time its threshold
    # is met, while offset keeps getting overwritten, so it ends up as
    # the time of the last frame that met the offset threshold.
    nFrames = Get number of frames
    onset = undefined
    offset = undefined

    for j from 1 to nFrames
        value = Get value in frame: j

        if value <> undefined
            if value >= onset_threshold_dB
                if onset = undefined
                    onset = Get time from frame number: j
                endif
            endif
            if value >= offset_threshold_dB
                offset = Get time from frame number: j
            endif
        endif
    endfor

    if onset <> undefined

        selectObject: sound
        Extract part: onset, endTime, "rectangular", 1, "no"
        trimmed = selected("Sound")

        # offset is in the original sound's time axis; shift it
        # into the trimmed sound's time axis.
        offsetInTrimmed = offset - onset

        # Trim off any trailing silence after the last detected speech.
        selectObject: trimmed
        Extract part: 0, offsetInTrimmed, "rectangular", 1, "no"
        final = selected("Sound")

        removeObject: trimmed

        selectObject: final
        Save as WAV file: output_folder$ + "/" + fileName$

        removeObject: final

    else
        printline fileName$, ": NO ONSET DETECTED"
    endif

    removeObject: intensity
    removeObject: sound

endfor

removeObject: fileList

printline "Done."