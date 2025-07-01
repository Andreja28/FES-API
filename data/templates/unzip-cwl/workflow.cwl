#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: CommandLineTool
baseCommand: [tar, -xf]
inputs:
  tarfile:
    type: File
    inputBinding:
      position: 1
outputs:
  file1:
    type: File
    outputBinding:
      glob: output.txt
  file2:
    type: File
    outputBinding:
      glob: touch.txt
  file3:
    type: File
    outputBinding:
      glob: file.txt