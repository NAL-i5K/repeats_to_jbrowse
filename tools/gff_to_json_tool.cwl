class: CommandLineTool
cwlVersion: v1.2

requirements:
    InlineJavascriptRequirement: {}

baseCommand:
    - singularity
    - exec

inputs:
    singularity_image:
        type: string
        inputBinding:
            position: 1

    in_gff:
        type: File
        inputBinding:
            prefix: --gff
            position: 3

    in_track_label:
        type: string
        inputBinding:
            prefix: --trackLabel
            position: 4

    in_json_directory:
        type: string
        inputBinding:
            prefix: --out
            position: 5

    in_track_key:
        type: string
        inputBinding:
            prefix: --key
            position: 6

    in_data_provider:
        type: string

    in_data_source:
        type: string

    in_materials_and_methods:
        type: string

    in_publication_status:
        type: string

arguments:
    - valueFrom: flatfile-to-json.pl
      position: 2
    - valueFrom: '{ "label": "name" ,  "description": "identity" }'
      prefix: --clientConfig
      position: 7
    - valueFrom: >
        ${
            return JSON.stringify({
                category: "Repeat Annotations",
                metadata: {
                    "Data description": "RepeatModeler annotations converted for JBrowse1",
                    "Data provider": inputs.in_data_provider,
                    "Data source": inputs.in_data_source,
                    "Materials and methods": inputs.in_materials_and_methods,
                    "Publication status": inputs.in_publication_status
                }
            });
        }
      prefix: --config
      position: 8

outputs:
    out_json_tracks:
        type: Directory
        outputBinding:
            glob: $(inputs.in_json_directory)
