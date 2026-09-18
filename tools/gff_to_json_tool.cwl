class: CommandLineTool
cwlVersion: v1.2

requirements:
    InlineJavascriptRequirement: {}

baseCommand:
    - python3

inputs:
    conversion_script:
        type: File
        default:
            class: File
            location: run-flatfile-to-json.py
        inputBinding:
            position: 1

    annotation_source:
        type: string
        inputBinding:
            position: 2

    singularity_image:
        type: string
        inputBinding:
            position: 3

    in_gff:
        type: File
        inputBinding:
            position: 4

    in_track_label:
        type: string
        inputBinding:
            position: 5

    in_json_directory:
        type: string
        default: repeatmodeler_json_tracks
        inputBinding:
            position: 6

    in_track_key:
        type: string
        inputBinding:
            position: 7

    in_data_provider:
        type: string
        inputBinding:
            position: 8

    in_data_source:
        type: string
        inputBinding:
            position: 9

    in_data_description:
        type: string
        inputBinding:
            position: 10

    in_materials_and_methods:
        type: string
        inputBinding:
            position: 11

    in_publication_status:
        type: string
        inputBinding:
            position: 12

outputs:
    out_json_tracks:
        type: Directory
        outputBinding:
            glob: $(inputs.in_json_directory)
