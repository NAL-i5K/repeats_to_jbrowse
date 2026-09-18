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

    in_gff:
        type: File
        inputBinding:
            position: 2

outputs:
    out_gff:
        type: File
        outputBinding:
            glob: remodeled.gff
