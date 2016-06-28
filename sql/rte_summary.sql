select 
                                    b.name,
                                    sum(num_surveys) as sum_survey,
                                    round(100*sum(num_surveys)/(select sum(num_surveys) from sroutes)::numeric,2) as pct 
                                    from sroutes a,surveyors b
                                    where a.surveyor = b.surveyor
                                    group by b.name
                                    order by sum_survey 

select 

r.rte_desc,
sum(s.num_surveys) as sum,
round(100*sum(num_surveys)/(select sum(num_surveys) from sroutes)::numeric,2) as pct

from sroutes s,rtedesc_lookup r
where s.rte = r.rte::varchar
group by r.rte_desc
order by sum desc;

