-- Insert script of agents
-- This script is used to create a default agent of gemini type

insert into agents (name, description, llm, reasoning, type_model, output_parser, instructions, has_storage, knowledge_collection_name, knowledge_description, knowledge_top_k)
select 'gemini default', 'Um agente padrão para o Gemini', 1, true, 'gemini-2.0-flash', null, null, false, null, null, 5
where not exists (
    select 1 from agents where name = 'gemini default' and llm = 1 and type_model = 'gemini-2.0-flash'
);
