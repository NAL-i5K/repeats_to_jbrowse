class: CommandLineTool
cwlVersion: v1.2

baseCommand:
    - python3

inputs:
    publish_script:
        type: File
        default:
            class: File
            location: publish-jbrowse-directory.py
        inputBinding:
            position: 1

    source_directory:
        type: Directory
        inputBinding:
            position: 2

    destination_directory:
        type:
            - "null"
            - string
        inputBinding:
            position: 3

outputs:
    out_publish_summary:
        type: File
        outputBinding:
            glob: publish-summary.json
