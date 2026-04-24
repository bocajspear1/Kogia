from backend.lib.plugin_base import PluginBase
from backend.lib.data import SIGNATURE_SEVERITY, Process
from backend.lib.job import Job, ExportFile
import tempfile
import io
import os

from datetime import datetime

class ExportTestPlugin(PluginBase):
    PLUGIN_TYPE = 'export'
    DESCRIPTION = "Export data to text format"
    VERSION = "0.0.1"

    def __init__(self, plugin_manager, args=None):
        super().__init__(plugin_manager)

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
        return "job.txt", "text/plain"
    
    def export(self, job_obj : Job, export_file : ExportFile):

        print(self.args)


        markdown_content = f"""
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
        _, instances = job_obj.get_exec_instances(as_obj=True, load_processes=True)
        for instance in instances:
            markdown_content += f"## {instance.exec_module}\n\n"
            for process in instance.processes:
                markdown_content += self._add_processes(process)

        markdown_content += "\n\n"

        markdown_content += "# Events\n\n"

        proc_map = {}
        
        for exec_inst, process in export_file.filtered_processes():
            markdown_content += f"## {process.command_line} - {process.pid}\n\n"
            markdown_content += "| Type | Source | Destination | Data                  | Success |\n"
            markdown_content += "| ---- | ------ | ----------- | --------------------- | ------- |\n"
            for _, _, event in export_file.filtered_events(process=process, exec_instance=exec_inst):
                markdown_content += f"| {event.key} | {event.src} | {event.dest} | {event.data} | {event.success} |\n"

                

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

        return True, markdown_content.encode()

    def check(self):
        pass


__PLUGIN__ = ExportTestPlugin