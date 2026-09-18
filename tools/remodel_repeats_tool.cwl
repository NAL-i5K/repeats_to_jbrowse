class: CommandLineTool
cwlVersion: v1.2

baseCommand:
    - python3

stdout: remodeled.gff

inputs:
    remodel_script:
        type: File
        default:
            class: File
            location: remodel-repeats.py
        inputBinding:
            position: 1

    annotation_source:
        type: string
        inputBinding:
            position: 2

    in_gff:
        type: File
        inputBinding:
            position: 3

outputs:
    out_gff:
        type: File
        outputBinding:
            glob: remodeled.gff
