-- Insert script of agents
-- This script is used to create a default agent of gemini type

insert into agents (name, description, llm, reasoning, type_model) values ('gemini default', 'Um agente padrão para o Gemini', 1, true, 'gemini-2.0-flash');
