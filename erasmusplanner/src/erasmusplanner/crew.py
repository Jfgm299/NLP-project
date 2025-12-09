from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import SerperDevTool
from typing import List
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class Erasmusplanner():
    """Erasmusplanner crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # ---------------------------------------------------------------------
    # AGENTS
    # ---------------------------------------------------------------------
    
    @agent
    def learning_coordinator(self) -> Agent:
        return Agent(
            config=self.agents_config['learning_coordinator'],
            verbose=True
        )

    @agent
    def home_university_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['home_university_researcher'],
            verbose=True,
            tools=[SerperDevTool()] # Giving this agent the ability to search the web
        )

    @agent
    def host_university_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['host_university_researcher'],
            verbose=True,
            tools=[SerperDevTool()] # Giving this agent the ability to search the web
        )

    @agent
    def subject_validator(self) -> Agent:
        return Agent(
            config=self.agents_config['subject_validator'],
            verbose=True
            # This agent relies on context from others, so it doesn't strictly need a search tool
        )

    # ---------------------------------------------------------------------
    # TASKS
    # ---------------------------------------------------------------------

    @task
    def collect_home_data(self) -> Task:
        return Task(
            config=self.tasks_config['collect_home_data'],
            human_input=True
        )

    @task
    def research_home_syllabus(self) -> Task:
        return Task(
            config=self.tasks_config['research_home_syllabus']
        )

    @task
    def collect_host_data(self) -> Task:
        return Task(
            config=self.tasks_config['collect_host_data'],
            human_input=True
        )

    @task
    def identify_host_courses(self) -> Task:
        return Task(
            config=self.tasks_config['identify_host_courses']
        )

    @task
    def fetch_host_syllabi(self) -> Task:
        return Task(
            config=self.tasks_config['fetch_host_syllabi']
        )

    @task
    def perform_validation_matrix(self) -> Task:
        return Task(
            config=self.tasks_config['perform_validation_matrix']
        )

    @task
    def generate_learning_agreement(self) -> Task:
        return Task(
            config=self.tasks_config['generate_learning_agreement']
        )

    @task
    def present_final_report(self) -> Task:
        return Task(
            config=self.tasks_config['present_final_report'],
            output_file='erasmus_learning_agreement.md' # Ensures the file is actually created
        )

    # ---------------------------------------------------------------------
    # CREW DEFINITION
    # ---------------------------------------------------------------------

    @crew
    def crew(self) -> Crew:
        """Creates the Erasmusplanner crew"""
        return Crew(
            agents=self.agents, # Automatically collects all @agent methods
            tasks=self.tasks,   # Automatically collects all @task methods
            process=Process.sequential,
            verbose=True,
            max_rpm=3
        )