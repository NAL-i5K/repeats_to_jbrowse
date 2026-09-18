cwlVersion: v1.2
class: Workflow

inputs:
    repeat_annotations: File
    singularity_image: string
    data_provider: string
    data_source: string
    materials_and_methods: string
    publication_status: string
    track_name: string
    jbrowse_directory:
        type:
            - "null"
            - string
        default: null

outputs:
    publish_summary:
        type: File
        outputSource: publish_json_tracks/out_publish_summary

steps:
    remodel_repeats:
        run:
            tools/remodel_repeats_tool.cwl
        in:
            in_gff: repeat_annotations
        out:
            [out_gff]

    convert_gff_to_json:
        run:
            tools/gff_to_json_tool.cwl
        in:
            singularity_image: singularity_image
            in_gff: remodel_repeats/out_gff
            in_data_provider: data_provider
            in_data_source: data_source
            in_materials_and_methods: materials_and_methods
            in_publication_status: publication_status
            in_track_label: track_name
            in_track_key: track_name
        out:
            [out_json_tracks]

    publish_json_tracks:
        run:
            tools/publish_jbrowse_directory_tool.cwl
        in:
            source_directory: convert_gff_to_json/out_json_tracks
            destination_directory: jbrowse_directory
        out:
            [out_publish_summary]
