--
-- PostgreSQL database dump
--

-- Dumped from database version 15.4
-- Dumped by pg_dump version 15.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: check_alert_quantity(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.check_alert_quantity() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.is_below_alert := NEW.quantity < NEW.alert_quantity;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.check_alert_quantity() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: belong_to_order; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.belong_to_order (
    order_id integer NOT NULL,
    product_id integer NOT NULL,
    quantity integer NOT NULL,
    CONSTRAINT belong_to_order_quantity_check CHECK ((quantity > 0))
);


ALTER TABLE public.belong_to_order OWNER TO postgres;

--
-- Name: carts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.carts (
    user_id integer NOT NULL,
    product_id integer NOT NULL,
    quantity integer NOT NULL,
    CONSTRAINT carts_quantity_check CHECK ((quantity > 0))
);


ALTER TABLE public.carts OWNER TO postgres;

--
-- Name: exporti_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.exporti_log (
    log_id integer NOT NULL,
    product_id integer,
    delta_quantity integer NOT NULL,
    change_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    changed_by character varying(255) NOT NULL
);


ALTER TABLE public.exporti_log OWNER TO postgres;

--
-- Name: exporti_log_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.exporti_log_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.exporti_log_log_id_seq OWNER TO postgres;

--
-- Name: exporti_log_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.exporti_log_log_id_seq OWNED BY public.exporti_log.log_id;


--
-- Name: importi_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.importi_log (
    log_id integer NOT NULL,
    product_id integer,
    delta_quantity integer NOT NULL,
    change_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    changed_by character varying(255) NOT NULL
);


ALTER TABLE public.importi_log OWNER TO postgres;

--
-- Name: importi_log_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.importi_log_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.importi_log_log_id_seq OWNER TO postgres;

--
-- Name: importi_log_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.importi_log_log_id_seq OWNED BY public.importi_log.log_id;


--
-- Name: inventory; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.inventory (
    product_id integer NOT NULL,
    product_name character varying(255) NOT NULL,
    quantity integer NOT NULL,
    price numeric(10,2) NOT NULL,
    alert_quantity integer NOT NULL,
    is_below_alert boolean DEFAULT false,
    sales integer DEFAULT 0 NOT NULL,
    discount numeric(3,2) DEFAULT 1.0,
    total_sales numeric(10,2) DEFAULT 0,
    CONSTRAINT inventory_alert_quantity_check CHECK ((alert_quantity >= 0)),
    CONSTRAINT inventory_discount_check CHECK (((discount >= (0)::numeric) AND (discount <= (1)::numeric))),
    CONSTRAINT inventory_price_check CHECK ((price >= (0)::numeric)),
    CONSTRAINT inventory_quantity_check CHECK ((quantity >= 0))
);


ALTER TABLE public.inventory OWNER TO postgres;

--
-- Name: inventory_product_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.inventory_product_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.inventory_product_id_seq OWNER TO postgres;

--
-- Name: inventory_product_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.inventory_product_id_seq OWNED BY public.inventory.product_id;


--
-- Name: orders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.orders (
    order_id integer NOT NULL,
    user_id integer NOT NULL,
    totalprice numeric(10,2) NOT NULL,
    orderdate timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.orders OWNER TO postgres;

--
-- Name: orders_order_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.orders_order_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.orders_order_id_seq OWNER TO postgres;

--
-- Name: orders_order_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.orders_order_id_seq OWNED BY public.orders.order_id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    user_id integer NOT NULL,
    username character varying(50) NOT NULL,
    password character varying(255) NOT NULL,
    sex character(1),
    birthday date,
    address text,
    phone character varying(20),
    email character varying(25),
    CONSTRAINT users_sex_check CHECK ((sex = ANY (ARRAY['M'::bpchar, 'F'::bpchar, 'O'::bpchar])))
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_user_id_seq OWNER TO postgres;

--
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;


--
-- Name: exporti_log log_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exporti_log ALTER COLUMN log_id SET DEFAULT nextval('public.exporti_log_log_id_seq'::regclass);


--
-- Name: importi_log log_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.importi_log ALTER COLUMN log_id SET DEFAULT nextval('public.importi_log_log_id_seq'::regclass);


--
-- Name: inventory product_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory ALTER COLUMN product_id SET DEFAULT nextval('public.inventory_product_id_seq'::regclass);


--
-- Name: orders order_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders ALTER COLUMN order_id SET DEFAULT nextval('public.orders_order_id_seq'::regclass);


--
-- Name: users user_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN user_id SET DEFAULT nextval('public.users_user_id_seq'::regclass);


--
-- Data for Name: belong_to_order; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.belong_to_order (order_id, product_id, quantity) FROM stdin;
5	55	1
5	45	1
5	49	1
5	53	1
5	57	1
5	60	1
5	56	1
5	31	1
6	46	1
6	47	1
6	48	1
6	50	1
6	51	1
6	52	1
6	59	1
7	54	1
7	69	1
7	67	1
8	70	1
8	71	1
8	72	1
9	62	1
9	61	1
9	14	1
10	32	1
11	64	1
12	68	1
13	46	1
18	46	2
19	46	2
26	31	1
27	46	1
27	47	1
27	49	1
27	32	1
27	45	1
27	31	1
28	31	100
38	31	100
39	31	100
40	45	122
41	32	230
42	45	1
\.


--
-- Data for Name: carts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.carts (user_id, product_id, quantity) FROM stdin;
\.


--
-- Data for Name: exporti_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exporti_log (log_id, product_id, delta_quantity, change_date, changed_by) FROM stdin;
4	31	-1	2024-06-24 18:42:35.074755	System
5	46	-1	2024-06-24 19:07:00.641465	System
6	47	-1	2024-06-24 19:07:00.643464	System
7	49	-1	2024-06-24 19:07:00.644464	System
8	32	-1	2024-06-24 19:07:00.645464	System
9	45	-1	2024-06-24 19:07:00.646465	System
10	31	-1	2024-06-24 19:07:00.647468	System
11	31	-100	2024-06-25 01:00:39.833264	System
12	31	-100	2024-06-25 01:11:01.421327	System
13	31	-100	2024-06-25 01:12:29.392205	System
14	45	-122	2024-06-25 11:10:47.877659	System
15	32	-230	2024-06-25 11:12:17.558765	System
16	45	-1	2024-06-25 11:14:19.340662	System
17	45	1	2024-06-25 14:02:41.600844	shadder3k
18	45	1	2024-06-25 14:02:48.440946	shadder3k
19	45	1	2024-06-25 14:02:54.466781	shadder3k
\.


--
-- Data for Name: importi_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.importi_log (log_id, product_id, delta_quantity, change_date, changed_by) FROM stdin;
1	14	9999	2024-01-01 11:49:26.0314	shadder3k
9	31	1231	2024-01-01 12:28:50.048457	query
10	32	1231	2024-01-01 12:33:04.199688	query
13	45	113	2024-01-01 14:11:16.230998	shadder3k
14	46	1	2024-06-22 23:02:44.151923	shadder3k
15	47	2	2024-06-22 23:02:50.568917	shadder3k
16	48	3	2024-06-22 23:04:28.725197	shadder3k
17	49	4	2024-06-22 23:04:34.387968	shadder3k
18	50	5	2024-06-22 23:04:39.403273	shadder3k
19	51	6	2024-06-22 23:04:44.082201	shadder3k
20	52	7	2024-06-22 23:04:52.256961	shadder3k
21	53	8	2024-06-22 23:04:58.781764	shadder3k
22	54	9	2024-06-22 23:05:04.749909	shadder3k
23	55	10	2024-06-22 23:05:11.878261	shadder3k
24	56	11	2024-06-22 23:05:20.847777	shadder3k
25	57	12	2024-06-22 23:05:31.330501	shadder3k
26	14	100	2024-06-24 21:19:34.138781	shadder3k
27	31	110	2024-06-24 21:19:40.064178	shadder3k
30	77	1	2024-06-25 00:29:23.811332	shadder3k
\.


--
-- Data for Name: inventory; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.inventory (product_id, product_name, quantity, price, alert_quantity, is_below_alert, sales, discount, total_sales) FROM stdin;
14	Database_Project	12345	0.00	13	f	1	1.00	0.00
31	围棋	1150	0.00	0	f	101	1.00	0.00
46	狼与香辛料1	100	0.00	0	f	6	1.00	0.00
32	完全胜利	1000	0.00	0	f	231	1.00	0.00
45	测试	3996	123.00	10000	t	124	1.00	12312.00
63	矿泉水	500	2.99	50	f	0	1.00	0.00
65	蛋糕	80	8.99	8	f	0	1.00	0.00
66	iPhone	50	9.99	5	f	0	0.10	0.00
73	面霜	100	45.99	10	f	0	1.00	0.00
74	雨伞	180	25.99	18	f	0	1.00	0.00
55	狼与香辛料10	10	0.00	0	f	1	1.00	0.00
53	狼与香辛料8	8	0.00	0	f	1	1.00	0.00
57	狼与香辛料12	12	0.00	0	f	1	1.00	0.00
60	方便面	200	7.99	20	f	1	0.90	0.00
56	狼与香辛料11	11	0.00	0	f	1	1.00	0.00
48	狼与香辛料3	3	0.00	0	f	1	1.00	0.00
50	狼与香辛料5	5	0.00	0	f	1	1.00	0.00
51	狼与香辛料6	6	0.00	0	f	1	1.00	0.00
52	狼与香辛料7	7	0.00	0	f	1	1.00	0.00
59	牛奶	100	32.80	10	f	1	1.00	0.00
54	狼与香辛料9	9	0.00	0	f	1	1.00	0.00
69	帽子	75	37.99	7	f	1	1.00	0.00
67	红楼梦	60	49.99	6	f	1	1.00	0.00
70	冰箱	30	99.99	3	f	1	1.00	0.00
71	消毒水	250	5.99	25	f	1	1.00	0.00
72	键盘	40	79.99	4	f	1	1.00	0.00
62	饼干	120	17.99	12	f	1	1.00	0.00
61	苹果	150	6.99	15	f	1	1.00	0.00
64	纸巾	300	27.99	30	f	1	1.00	0.00
68	牙刷	200	10.99	20	f	1	1.00	0.00
47	狼与香辛料2	1	0.00	0	f	1	1.00	0.00
49	狼与香辛料4	3	0.00	0	f	1	1.00	0.00
77	Ciri	1	0.00	10	t	0	1.00	0.00
\.


--
-- Data for Name: orders; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.orders (order_id, user_id, totalprice, orderdate) FROM stdin;
5	11	12319.19	2024-06-24 12:23:34
6	11	32.80	2024-06-24 12:24:08
7	11	87.98	2024-06-24 12:28:55
8	11	185.97	2024-06-24 12:29:18
9	11	24.98	2024-06-24 12:40:22
10	11	0.00	2024-06-24 12:41:10
11	11	27.99	2024-06-24 12:41:30
12	11	10.99	2024-06-24 12:42:42
13	11	0.00	2024-06-24 15:01:39
18	11	0.00	2024-06-24 15:16:02
19	11	0.00	2024-06-24 15:16:17
26	11	0.00	2024-06-24 18:42:35
27	11	12312.00	2024-06-24 19:07:00
28	11	0.00	2024-06-25 01:00:39
38	11	0.00	2024-06-25 01:11:01
39	11	0.00	2024-06-25 01:12:29
40	11	1502064.00	2024-06-25 11:10:47
41	11	0.00	2024-06-25 11:12:17
42	11	12312.00	2024-06-25 11:14:19
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (user_id, username, password, sex, birthday, address, phone, email) FROM stdin;
11	shadder3k_user	612ede8edd342618d3b19bb7bd7b699858aab5a8659aaa4ae44956caf3574fe9	M	2004-01-31	中山大学东校园	13709606654	2930769989@qq.com
\.


--
-- Name: exporti_log_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.exporti_log_log_id_seq', 19, true);


--
-- Name: importi_log_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.importi_log_log_id_seq', 30, true);


--
-- Name: inventory_product_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.inventory_product_id_seq', 77, true);


--
-- Name: orders_order_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.orders_order_id_seq', 42, true);


--
-- Name: users_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_user_id_seq', 15, true);


--
-- Name: belong_to_order belong_to_order_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.belong_to_order
    ADD CONSTRAINT belong_to_order_pkey PRIMARY KEY (order_id, product_id);


--
-- Name: carts carts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.carts
    ADD CONSTRAINT carts_pkey PRIMARY KEY (user_id, product_id);


--
-- Name: exporti_log exporti_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exporti_log
    ADD CONSTRAINT exporti_log_pkey PRIMARY KEY (log_id);


--
-- Name: importi_log importi_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.importi_log
    ADD CONSTRAINT importi_log_pkey PRIMARY KEY (log_id);


--
-- Name: inventory inventory_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_pkey PRIMARY KEY (product_id);


--
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (order_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: inventory check_alert_quantity_before_insert_or_update; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER check_alert_quantity_before_insert_or_update BEFORE INSERT OR UPDATE ON public.inventory FOR EACH ROW EXECUTE FUNCTION public.check_alert_quantity();


--
-- Name: belong_to_order belong_to_order_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.belong_to_order
    ADD CONSTRAINT belong_to_order_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(order_id);


--
-- Name: carts carts_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.carts
    ADD CONSTRAINT carts_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.inventory(product_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: carts carts_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.carts
    ADD CONSTRAINT carts_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: exporti_log exporti_log_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exporti_log
    ADD CONSTRAINT exporti_log_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.inventory(product_id) ON DELETE CASCADE;


--
-- Name: importi_log importi_log_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.importi_log
    ADD CONSTRAINT importi_log_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.inventory(product_id) ON DELETE CASCADE;


--
-- Name: orders orders_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- PostgreSQL database dump complete
--

