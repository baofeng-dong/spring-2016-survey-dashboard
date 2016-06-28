--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public,pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: scount; Type: TABLE; Schema: odk; Owner: -; Tablespace: 
--

CREATE TABLE scount (
    id serial primary key ,
    surveyor text,
    willing text,
    count bigint,
    pct_surveyor numeric,
    pct numeric
);


--
-- Data for Name: scount; Type: TABLE DATA; Schema: odk; Owner: -
--

COPY scount (surveyor, willing, count, pct_surveyor, pct) FROM stdin;
aborja	Yes	543	65.34	2.00
aborja	No	288	34.66	1.06
aboyce	Yes	849	74.60	3.13
aboyce	No	254	22.32	0.94
aboyce	Incomplete	35	3.08	0.13
asalazar	Yes	357	70.83	1.32
asalazar	No	145	28.77	0.53
asalazar	Incomplete	2	0.40	0.01
aweinmann	Yes	142	54.62	0.52
aweinmann	No	118	45.38	0.44
cbehrens	Yes	2123	57.49	7.83
cbehrens	No	1531	41.46	5.65
cbehrens	Incomplete	39	1.06	0.14
dbarker	Yes	370	68.27	1.36
dbarker	No	161	29.70	0.59
dbarker	Incomplete	11	2.03	0.04
gkeeney	Yes	812	53.53	3.00
gkeeney	No	705	46.47	2.60
gwalker	Yes	39	56.52	0.14
gwalker	No	30	43.48	0.11
jemmons	Yes	1534	52.44	5.66
jemmons	No	1347	46.05	4.97
jemmons	Incomplete	44	1.50	0.16
jlamacchio	Yes	1312	54.19	4.84
jlamacchio	No	1077	44.49	3.97
jlamacchio	Incomplete	32	1.32	0.12
kcook	Yes	1816	76.95	6.70
kcook	No	495	20.97	1.83
kcook	Incomplete	49	2.08	0.18
kmarenger	Yes	437	68.28	1.61
kmarenger	No	198	30.94	0.73
kmarenger	Incomplete	5	0.78	0.02
kopitz	Yes	491	77.69	1.81
kopitz	No	130	20.57	0.48
kopitz	Incomplete	11	1.74	0.04
ktaber	Yes	2572	70.23	9.49
ktaber	No	935	25.53	3.45
ktaber	Incomplete	155	4.23	0.57
mobrien	Yes	601	77.05	2.22
mobrien	No	138	17.69	0.51
mobrien	Incomplete	41	5.26	0.15
mplumer	Yes	2114	74.73	7.80
mplumer	No	607	21.46	2.24
mplumer	Incomplete	108	3.82	0.40
sharris	Yes	697	80.67	2.57
sharris	No	152	17.59	0.56
sharris	Incomplete	15	1.74	0.06
srogers	Yes	61	87.14	0.23
srogers	No	9	12.86	0.03
tsolmon	Yes	186	62.63	0.69
tsolmon	No	110	37.04	0.41
tsolmon	Incomplete	1	0.34	0.00
tsubrin	Yes	676	62.88	2.49
tsubrin	No	378	35.16	1.39
tsubrin	Incomplete	21	1.95	0.08
\.


--
-- PostgreSQL database dump complete
--

