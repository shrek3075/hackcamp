--
-- PostgreSQL database dump
--


-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.7

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--



--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    SET search_path TO 'public'
    AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$;


SET default_table_access_method = heap;

--
-- Name: notes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.notes (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    subject text NOT NULL,
    title text NOT NULL,
    content text NOT NULL,
    archived boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: study_plans; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.study_plans (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    subject text NOT NULL,
    test_date date NOT NULL,
    busy_days text[] DEFAULT '{}'::text[],
    total_study_hours integer NOT NULL,
    syllabus_content text,
    plan_data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    completed boolean DEFAULT false,
    topic text
);


--
-- Name: topic_achievements; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.topic_achievements (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    subject text NOT NULL,
    topic_name text NOT NULL,
    achieved boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    unit_topic text
);


--
-- Name: notes notes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notes
    ADD CONSTRAINT notes_pkey PRIMARY KEY (id);


--
-- Name: study_plans study_plans_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.study_plans
    ADD CONSTRAINT study_plans_pkey PRIMARY KEY (id);


--
-- Name: topic_achievements topic_achievements_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.topic_achievements
    ADD CONSTRAINT topic_achievements_pkey PRIMARY KEY (id);


--
-- Name: topic_achievements topic_achievements_user_id_subject_topic_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.topic_achievements
    ADD CONSTRAINT topic_achievements_user_id_subject_topic_name_key UNIQUE (user_id, subject, topic_name);


--
-- Name: idx_study_plans_completed; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_study_plans_completed ON public.study_plans USING btree (completed);


--
-- Name: notes update_notes_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_notes_updated_at BEFORE UPDATE ON public.notes FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: study_plans update_study_plans_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_study_plans_updated_at BEFORE UPDATE ON public.study_plans FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: topic_achievements update_topic_achievements_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_topic_achievements_updated_at BEFORE UPDATE ON public.topic_achievements FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: notes Users can create their own notes; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can create their own notes" ON public.notes FOR INSERT WITH CHECK ((auth.uid() = user_id));


--
-- Name: study_plans Users can create their own study plans; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can create their own study plans" ON public.study_plans FOR INSERT WITH CHECK ((auth.uid() = user_id));


--
-- Name: topic_achievements Users can create their own topic achievements; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can create their own topic achievements" ON public.topic_achievements FOR INSERT WITH CHECK ((auth.uid() = user_id));


--
-- Name: notes Users can delete their own notes; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can delete their own notes" ON public.notes FOR DELETE USING ((auth.uid() = user_id));


--
-- Name: study_plans Users can delete their own study plans; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can delete their own study plans" ON public.study_plans FOR DELETE USING ((auth.uid() = user_id));


--
-- Name: topic_achievements Users can delete their own topic achievements; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can delete their own topic achievements" ON public.topic_achievements FOR DELETE USING ((auth.uid() = user_id));


--
-- Name: notes Users can update their own notes; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can update their own notes" ON public.notes FOR UPDATE USING ((auth.uid() = user_id));


--
-- Name: study_plans Users can update their own study plans; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can update their own study plans" ON public.study_plans FOR UPDATE USING ((auth.uid() = user_id));


--
-- Name: topic_achievements Users can update their own topic achievements; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can update their own topic achievements" ON public.topic_achievements FOR UPDATE USING ((auth.uid() = user_id));


--
-- Name: notes Users can view their own notes; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view their own notes" ON public.notes FOR SELECT USING ((auth.uid() = user_id));


--
-- Name: study_plans Users can view their own study plans; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view their own study plans" ON public.study_plans FOR SELECT USING ((auth.uid() = user_id));


--
-- Name: topic_achievements Users can view their own topic achievements; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view their own topic achievements" ON public.topic_achievements FOR SELECT USING ((auth.uid() = user_id));


--
-- Name: notes; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.notes ENABLE ROW LEVEL SECURITY;

--
-- Name: study_plans; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.study_plans ENABLE ROW LEVEL SECURITY;

--
-- Name: topic_achievements; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.topic_achievements ENABLE ROW LEVEL SECURITY;

--
-- PostgreSQL database dump complete
--


