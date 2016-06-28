--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: rtedesc_lookup; Type: TABLE; Schema: web; Owner: -; Tablespace: 
--

CREATE TABLE rtedesc_lookup (
    rte smallint,
    rte_desc character varying(50),
    in_dir smallint,
    in_dir_desc character varying(50),
    out_dir smallint,
    out_dir_desc character varying(50)
);


--
-- PostgreSQL database dump complete
--

