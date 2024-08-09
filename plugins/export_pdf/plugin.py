from backend.lib.plugin_base import DockerPluginBase
from backend.lib.data import SIGNATURE_SEVERITY, Process
from backend.lib.job import Job, ExportFile
import tempfile
import io
import os

from datetime import datetime

class ExportPDFPlugin(DockerPluginBase):
    PLUGIN_TYPE = 'export'
    DESCRIPTION = "Export data to PDF format"
    VERSION = "0.0.1"
    DOCKER_IMAGE = 'export_pdf'

    def __init__(self, plugin_manager, args=None):
        super().__init__(self.DOCKER_IMAGE, plugin_manager)

        if args is not None:
            self.args = args
        else:
            self.args = {}

    def _add_processes(self, process : Process, depth=0):
        return_data = ("  " * depth) + "- `" + process.command_line.replace('\\', '\\\\') + f" ({process.pid})`\n"
        for child in process.child_processes:
            return_data += self._add_processes(child, depth=depth+1)
        return return_data

    def get_export_metadata(self):
        return "job.pdf", "application/pdf"
    
    def export(self, job_obj : Job, export_file : ExportFile):

        print(self.args)


        markdown_content = f"""
---
title: "{self.args['title']}"
author: [{self.args['author']}]
date: "{datetime.now().strftime('%Y-%m-%d')}"
"""

        markdown_content += """lang: "en"
titlepage: true
header-includes:
- |
  ```{=latex}
  \\usepackage{awesomebox}
  ```
pandoc-latex-environment:
  noteblock: [note]
  tipblock: [tip]
  warningblock: [warning]
  cautionblock: [caution]
  importantblock: [important]
...

"""

        markdown_content += "# Introduction\n\n"

        markdown_content += f"{self.args['introduction']}\n\n"

        markdown_content += "# Primary File\n\n"

        primary_file = job_obj.get_primary_file()
        markdown_content += f"## {primary_file.name}\n\n"
        markdown_content += f"_{primary_file.hash}_\n\n"
        if primary_file.mime_type:
            markdown_content += f" - **MIME**: {primary_file.mime_type}\n"
        if primary_file.exec_type:
            markdown_content += f" - **Execution Type**: {primary_file.exec_type}\n"
        if primary_file.exec_arch and primary_file.exec_bits:
            markdown_content += f" - **Architecture**: {primary_file.exec_arch}, {primary_file.exec_bits}\n"
        if primary_file.exec_format:
            markdown_content += f" - **Format**: {primary_file.exec_format}\n"
        if primary_file.exec_packer:
            markdown_content += f" - **Packer**: {primary_file.exec_packer}\n"
        if primary_file.exec_interpreter:
            markdown_content += f" - **Interpreter**: {primary_file.exec_interpreter}\n"
        
        markdown_content += "\n\n"
        markdown_content += "# Signatures\n\n"
        for signature in export_file.signatures():
            if signature.severity == SIGNATURE_SEVERITY.INFO:
                markdown_content += "::: note\n"
            elif signature.severity == SIGNATURE_SEVERITY.CAUTION:
                markdown_content += "::: warning\n"
            elif signature.severity == SIGNATURE_SEVERITY.SUSPICIOUS:
                markdown_content += "::: caution\n"
            elif signature.severity == SIGNATURE_SEVERITY.MALICIOUS:
                markdown_content += "::: important\n"
            markdown_content += f"**{signature.name}**\n\n"
            markdown_content += f"{signature.description}\n"
            markdown_content += ":::\n"

        markdown_content += "# Processes\n\n"
        for instance in job_obj.get_exec_instances(as_obj=True):
            markdown_content += f"## {instance.exec_module}\n\n"
            for process in instance.processes:
                markdown_content += self._add_processes(process)

        markdown_content += "\n\n"

        # for exec_inst, process, event in export_file.events():
        #     print(exec_inst, process.command_line, event)

        markdown_content += "# Network Communications\n\n"
        markdown_content += "| Protocol | Source | Destination | Data            |\n"
        markdown_content += "| -------- | ------ | ----------- | --------------- |\n"
        for exec_inst, network_comm in export_file.network_comms():
            markdown_content += f"| {network_comm.protocol} | {network_comm.src_addr}:{network_comm.src_port} | {network_comm.dest_addr}:{network_comm.dest_port} | `{network_comm.data}` |\n"
        markdown_content += "\n\n"

        if export_file.has_files():
            markdown_content += "# Files\n\n"
            for file_obj in export_file.files():
                if not file_obj.dropped and file_obj.hash != primary_file.hash:
                    markdown_content += "## " + file_obj.name + "\n\n"
                    markdown_content += "_" + file_obj.hash + "_\n\n"
                    markdown_content += " - MIME: " + file_obj.mime_type + "\n\n"

            for file_obj in export_file.files():
                if file_obj.dropped and file_obj.hash != primary_file.hash:
                    markdown_content += "## " + file_obj.name + " (Dropped)\n\n"
                    markdown_content += "_" + file_obj.hash + "_\n\n"
                    markdown_content += " - MIME: " + file_obj.mime_type + "\n\n"

    
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chmod(temp_dir, 0o755)
            outfile = tempfile.NamedTemporaryFile("w", suffix=".md", dir=temp_dir)
            os.chmod(outfile.name, 0o777)
            print(outfile.name)
            outfile.write(markdown_content)
            outfile.flush()

            self.run_image(str(temp_dir), job_obj, outfile.name)
            self.wait_and_stop()

            outfile.close()

            pdf_output = self.extract_single_file_to(str(temp_dir), "/tmp/output.pdf", bin=True)


            self.remove_tmp_dirs()
            self.remove_container(job_obj)

            return True, pdf_output

    def check(self):
        pass


__PLUGIN__ = ExportPDFPlugin