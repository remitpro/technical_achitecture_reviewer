from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, task, crew
from technical_reviewer.tools.document_parser import parse_document
from technical_reviewer.tools.report_generator import generate_report

@CrewBase
class TechnicalReviewerCrew:
    """Technical Reviewer crew"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def document_processor(self) -> Agent:
        return Agent(
            config=self.agents_config['document_processor'],
            tools=[parse_document],
            verbose=True
        )

    @agent
    def enterprise_architect(self) -> Agent:
        return Agent(
            config=self.agents_config['enterprise_architect'],
            verbose=True
        )

    @agent
    def security_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['security_analyst'],
            verbose=True
        )

    @agent
    def compliance_officer(self) -> Agent:
        return Agent(
            config=self.agents_config['compliance_officer'],
            verbose=True
        )

    @agent
    def devops_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['devops_engineer'],
            verbose=True
        )

    @agent
    def report_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['report_writer'],
            tools=[generate_report],
            verbose=True
        )

    @task
    def parse_document(self) -> Task:
        return Task(
            config=self.tasks_config['parse_document'],
            agent=self.document_processor()
        )

    @task
    def architecture_review(self) -> Task:
        return Task(
            config=self.tasks_config['architecture_review'],
            agent=self.enterprise_architect()
        )

    @task
    def security_review(self) -> Task:
        return Task(
            config=self.tasks_config['security_review'],
            agent=self.security_analyst()
        )

    @task
    def compliance_review(self) -> Task:
        return Task(
            config=self.tasks_config['compliance_review'],
            agent=self.compliance_officer()
        )

    @task
    def devops_review(self) -> Task:
        return Task(
            config=self.tasks_config['devops_review'],
            agent=self.devops_engineer()
        )

    @task
    def gap_analysis(self) -> Task:
        return Task(
            config=self.tasks_config['gap_analysis'],
            agent=self.enterprise_architect()
        )

    @task
    def final_report(self) -> Task:
        return Task(
            config=self.tasks_config['final_report'],
            agent=self.report_writer()
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
