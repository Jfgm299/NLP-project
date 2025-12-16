import panel as pn
from typing import List

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import SerperDevTool, PDFSearchTool, ScrapeWebsiteTool
from crewai.tasks.task_output import TaskOutput

from erasmusplanner.tools.human_input_tool import HumanInputTool
from erasmusplanner.tools.validation_tool import ValidationMatrixTool
from crewai.rag.embeddings.providers.google.types import VertexAIProviderSpec

vertex_embedder = VertexAIProviderSpec(
    provider="google-vertex",
    config={
        "model_name": "text-embedding-004",
        "project_id": "nlp-project-480912",
        "region": "us-central1",
    }
)


# ---------------------------------------------------------------------
# CONFIGURACIÓN DE HERRAMIENTAS PDF (RAG)
# ---------------------------------------------------------------------
# Definimos la configuración para que el PDFSearchTool use Gemini y no OpenAI
pdf_rag_config = {
    "embedding_model": {
        "provider": "google-vertex",  # Use google-vertex, not google
        "config": {
            "model_name": "text-embedding-004",
            "project_id": "nlp-project-480912",
            "region": "us-central1",
        },
    },
    "vectordb": {
        "provider": "chromadb",
        "config": {}
    },
}

pdf_tool_subjects = PDFSearchTool(
    pdf='../../knowledge/home_degree_subjects.pdf',
    config=pdf_rag_config
)


# ---------------------------------------------------------------------
# UI OUTPUT HANDLER
# ---------------------------------------------------------------------

# ✅ FIX: stretch_both is required so it fills the CSS card
chat_interface = pn.chat.ChatInterface(sizing_mode="stretch_both")

chat_interface.show_clear = False
chat_interface.show_undo = False
chat_interface.show_rerun = False

def print_output(output: TaskOutput):
    """Envía la salida de la tarea al chat."""
    message = output.raw
    chat_interface.send(
        message,
        user=output.agent,
        respond=False
    )

# ---------------------------------------------------------------------
# CREW DEFINITION
# ---------------------------------------------------------------------

@CrewBase
class Erasmusplanner():
    """Erasmusplanner Crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # --- AGENTS ---
    @agent
    def learning_coordinator(self) -> Agent:
        return Agent(config=self.agents_config['learning_coordinator'], verbose=True, tools=[HumanInputTool()])

    @agent
    def home_university_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['home_university_researcher'],
            verbose=True, tools=[pdf_tool_subjects])

    @agent
    def host_university_researcher(self) -> Agent:
        return Agent(config=self.agents_config['host_university_researcher'], verbose=True, tools=[SerperDevTool(),ScrapeWebsiteTool()])

    @agent
    def subject_validator(self) -> Agent:
        return Agent(config=self.agents_config['subject_validator'], verbose=True, tools=[ValidationMatrixTool()])

    # --- TASKS ---
    @task
    def collect_home_data(self) -> Task:
        return Task(config=self.tasks_config['collect_home_data'], callback=print_output)

    @task
    def research_home_syllabus(self) -> Task:
        return Task(config=self.tasks_config['research_home_syllabus'], callback=print_output)

    @task
    def confirm_home_subjects(self) -> Task:
        return Task(config=self.tasks_config['confirm_home_subjects'], callback=print_output)

    @task
    def collect_host_data(self) -> Task:
        return Task(config=self.tasks_config['collect_host_data'], callback=print_output)

    @task
    def identify_host_courses(self) -> Task:
        return Task(config=self.tasks_config['identify_host_courses'], callback=print_output)

    @task
    def fetch_host_syllabi(self) -> Task:
        return Task(config=self.tasks_config['fetch_host_syllabi'], callback=print_output)

    @task
    def perform_validation_matrix(self) -> Task:
        return Task(config=self.tasks_config['perform_validation_matrix'], callback=print_output)

    @task
    def generate_learning_agreement(self) -> Task:
        return Task(config=self.tasks_config['generate_learning_agreement'], callback=print_output)

    @task
    def present_final_report(self) -> Task:
        return Task(config=self.tasks_config['present_final_report'], output_file='erasmus_data.json', callback=print_output)

    @crew
    def crew(self) -> Crew:
        c = Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            embedder=vertex_embedder,
            memory=True
        )
        # ✅ Clear memory before starting the new chat
        c.reset_memories(command_type='short')
        c.reset_memories(command_type='long')
        return c
    
    
