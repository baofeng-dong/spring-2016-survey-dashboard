--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: sroutes; Type: TABLE; Schema: odk; Owner: -; Tablespace: 
--

CREATE TABLE sroutes (
    id serial primary key ,
    surveyor text,
    rte character varying(255),
    num_surveys bigint,
    pct_rte numeric,
    pct numeric
);


--
-- Data for Name: sroutes; Type: TABLE DATA; Schema: odk; Owner: -
--

COPY sroutes (surveyor, rte, num_surveys, pct_rte, pct) FROM stdin;
aborja	4	76	8.71	0.43
aborja	8	64	17.44	0.36
aborja	15	14	2.69	0.08
aborja	20	28	4.88	0.16
aborja	57	44	10.63	0.25
aborja	70	24	9.30	0.14
aborja	71	31	8.36	0.17
aborja	72	54	7.58	0.30
aborja	90	59	4.91	0.33
aborja	100	43	1.30	0.24
aborja	190	31	4.75	0.17
aborja	203	54	45.76	0.30
aborja	290	21	3.72	0.12
aboyce	4	59	6.76	0.33
aboyce	6	68	21.12	0.38
aboyce	9	67	12.25	0.38
aboyce	12	76	14.37	0.43
aboyce	15	63	12.09	0.36
aboyce	20	43	7.49	0.24
aboyce	52	42	17.00	0.24
aboyce	72	43	6.04	0.24
aboyce	90	90	7.49	0.51
aboyce	100	58	1.76	0.33
aboyce	190	57	8.73	0.32
aboyce	200	121	12.22	0.68
aboyce	290	62	10.97	0.35
asalazar	4	31	3.55	0.17
asalazar	17	27	5.17	0.15
asalazar	33	31	8.76	0.17
asalazar	62	40	18.02	0.23
asalazar	190	110	16.85	0.62
asalazar	200	52	5.25	0.29
asalazar	290	66	11.68	0.37
aweinmann	190	56	8.58	0.32
aweinmann	200	5	0.51	0.03
aweinmann	290	81	14.34	0.46
cbehrens	4	177	20.27	1.00
cbehrens	9	41	7.50	0.23
cbehrens	14	71	20.17	0.40
cbehrens	15	292	56.05	1.65
cbehrens	19	220	53.27	1.24
cbehrens	20	67	11.67	0.38
cbehrens	24	31	100.00	0.17
cbehrens	32	32	100.00	0.18
cbehrens	33	53	14.97	0.30
cbehrens	70	72	27.91	0.41
cbehrens	71	66	17.79	0.37
cbehrens	72	47	6.60	0.27
cbehrens	75	68	10.27	0.38
cbehrens	77	28	8.26	0.16
cbehrens	79	28	35.90	0.16
cbehrens	80	27	100.00	0.15
cbehrens	93	11	50.00	0.06
cbehrens	94	22	37.29	0.12
cbehrens	100	370	11.22	2.09
cbehrens	152	25	100.00	0.14
cbehrens	155	31	48.44	0.17
cbehrens	190	63	9.65	0.36
cbehrens	200	209	21.11	1.18
cbehrens	290	72	12.74	0.41
dbarker	8	22	5.99	0.12
dbarker	12	45	8.51	0.25
dbarker	15	27	5.18	0.15
dbarker	21	18	17.82	0.10
dbarker	45	37	100.00	0.21
dbarker	54	23	15.23	0.13
dbarker	56	21	13.13	0.12
dbarker	58	41	100.00	0.23
dbarker	90	29	2.41	0.16
dbarker	93	11	50.00	0.06
dbarker	94	37	62.71	0.21
dbarker	100	59	1.79	0.33
gkeeney	90	119	9.90	0.67
gkeeney	100	692	20.98	3.90
gkeeney	290	1	0.18	0.01
gwalker	190	28	4.29	0.16
gwalker	290	11	1.95	0.06
jemmons	4	170	19.47	0.96
jemmons	8	42	11.44	0.24
jemmons	9	82	14.99	0.46
jemmons	10	52	56.52	0.29
jemmons	12	210	39.70	1.18
jemmons	15	66	12.67	0.37
jemmons	19	32	7.75	0.18
jemmons	30	25	100.00	0.14
jemmons	33	54	15.25	0.30
jemmons	57	67	16.18	0.38
jemmons	70	51	19.77	0.29
jemmons	72	254	35.67	1.43
jemmons	75	125	18.88	0.71
jemmons	78	39	22.67	0.22
jemmons	87	19	100.00	0.11
jemmons	90	82	6.82	0.46
jemmons	100	87	2.64	0.49
jemmons	200	77	7.78	0.43
jlamacchio	4	56	6.41	0.32
jlamacchio	9	70	12.80	0.39
jlamacchio	14	96	27.27	0.54
jlamacchio	17	73	13.98	0.41
jlamacchio	19	91	22.03	0.51
jlamacchio	33	55	15.54	0.31
jlamacchio	71	208	56.06	1.17
jlamacchio	72	94	13.20	0.53
jlamacchio	75	104	15.71	0.59
jlamacchio	79	24	30.77	0.14
jlamacchio	90	67	5.57	0.38
jlamacchio	100	90	2.73	0.51
jlamacchio	155	24	37.50	0.14
jlamacchio	190	47	7.20	0.27
jlamacchio	200	164	16.57	0.93
jlamacchio	290	49	8.67	0.28
kcook	6	131	40.68	0.74
kcook	9	60	10.97	0.34
kcook	20	131	22.82	0.74
kcook	33	25	7.06	0.14
kcook	47	31	75.61	0.17
kcook	48	24	47.06	0.14
kcook	52	85	34.41	0.48
kcook	54	80	52.98	0.45
kcook	56	95	59.38	0.54
kcook	57	63	15.22	0.36
kcook	67	30	100.00	0.17
kcook	71	24	6.47	0.14
kcook	72	73	10.25	0.41
kcook	75	94	14.20	0.53
kcook	76	97	46.63	0.55
kcook	78	49	28.49	0.28
kcook	88	71	100.00	0.40
kcook	90	131	10.90	0.74
kcook	100	423	12.83	2.39
kcook	190	21	3.22	0.12
kcook	200	46	4.65	0.26
kcook	290	32	5.66	0.18
kmarenger	9	153	27.97	0.86
kmarenger	35	88	29.93	0.50
kmarenger	44	81	27.93	0.46
kmarenger	90	71	5.91	0.40
kmarenger	190	15	2.30	0.08
kmarenger	290	28	4.96	0.16
kopitz	4	42	4.81	0.24
kopitz	19	70	16.95	0.39
kopitz	22	24	100.00	0.14
kopitz	23	9	100.00	0.05
kopitz	25	6	100.00	0.03
kopitz	90	11	0.92	0.06
kopitz	96	51	100.00	0.29
kopitz	99	23	100.00	0.13
kopitz	100	175	5.31	0.99
kopitz	200	80	8.08	0.45
ktaber	4	262	30.01	1.48
ktaber	9	74	13.53	0.42
ktaber	12	76	14.37	0.43
ktaber	14	124	35.23	0.70
ktaber	15	1	0.19	0.01
ktaber	17	368	70.50	2.08
ktaber	20	137	23.87	0.77
ktaber	21	83	82.18	0.47
ktaber	33	67	18.93	0.38
ktaber	35	120	40.82	0.68
ktaber	44	73	25.17	0.41
ktaber	62	131	59.01	0.74
ktaber	70	66	25.58	0.37
ktaber	72	61	8.57	0.34
ktaber	75	164	24.77	0.93
ktaber	76	64	30.77	0.36
ktaber	77	91	26.84	0.51
ktaber	78	30	17.44	0.17
ktaber	90	100	8.32	0.56
ktaber	100	416	12.61	2.35
ktaber	200	64	6.46	0.36
mobrien	6	84	26.09	0.47
mobrien	12	42	7.94	0.24
mobrien	33	36	10.17	0.20
mobrien	72	42	5.90	0.24
mobrien	75	46	6.95	0.26
mobrien	100	28	0.85	0.16
mobrien	190	153	23.43	0.86
mobrien	200	90	9.09	0.51
mobrien	290	80	14.16	0.45
mplumer	8	239	65.12	1.35
mplumer	12	80	15.12	0.45
mplumer	16	43	100.00	0.24
mplumer	20	41	7.14	0.23
mplumer	35	86	29.25	0.49
mplumer	46	8	100.00	0.05
mplumer	47	10	24.39	0.06
mplumer	48	27	52.94	0.15
mplumer	52	77	31.17	0.43
mplumer	54	48	31.79	0.27
mplumer	56	44	27.50	0.25
mplumer	57	165	39.86	0.93
mplumer	62	51	22.97	0.29
mplumer	76	47	22.60	0.27
mplumer	77	71	20.94	0.40
mplumer	78	54	31.40	0.30
mplumer	90	308	25.62	1.74
mplumer	100	603	18.28	3.40
mplumer	190	20	3.06	0.11
mplumer	203	64	54.24	0.36
mplumer	290	26	4.60	0.15
sharris	10	40	43.48	0.23
sharris	15	57	10.94	0.32
sharris	17	54	10.34	0.30
sharris	20	1	0.17	0.01
sharris	44	136	46.90	0.77
sharris	77	56	16.52	0.32
sharris	90	135	11.23	0.76
sharris	100	48	1.46	0.27
sharris	190	52	7.96	0.29
sharris	200	82	8.28	0.46
sharris	290	36	6.37	0.20
srogers	20	61	10.63	0.34
tsolmon	52	43	17.41	0.24
tsolmon	57	30	7.25	0.17
tsolmon	77	20	5.90	0.11
tsolmon	100	93	2.82	0.52
tsubrin	6	39	12.11	0.22
tsubrin	14	61	17.33	0.34
tsubrin	15	1	0.19	0.01
tsubrin	20	65	11.32	0.37
tsubrin	33	33	9.32	0.19
tsubrin	36	11	100.00	0.06
tsubrin	37	8	100.00	0.05
tsubrin	57	45	10.87	0.25
tsubrin	70	45	17.44	0.25
tsubrin	71	42	11.32	0.24
tsubrin	72	44	6.18	0.25
tsubrin	75	61	9.21	0.34
tsubrin	77	73	21.53	0.41
tsubrin	79	26	33.33	0.15
tsubrin	100	113	3.43	0.64
tsubrin	155	9	14.06	0.05
\.


--
-- PostgreSQL database dump complete
--

