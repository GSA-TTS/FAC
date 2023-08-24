#lang racket

(define schema 'api_historic_v0_1_0_alpha)

(define tables
  '(census_agency16
    census_agency17
    census_agency18
    census_agency19
    census_agency20
    census_agency21
    census_agency22
    census_captext19
    census_captext20
    census_captext21
    census_captext22
    census_captext_formatted19
    census_captext_formatted20
    census_captext_formatted21
    census_captext_formatted22
    census_cfda16
    census_cfda17
    census_cfda18
    census_cfda19
    census_cfda20
    census_cfda21
    census_cfda22
    census_cpas16
    census_cpas17
    census_cpas18
    census_cpas19
    census_cpas20
    census_cpas21
    census_cpas22
    census_duns16
    census_duns17
    census_duns18
    census_duns19
    census_duns20
    census_duns21
    census_duns22
    census_eins16
    census_eins17
    census_eins18
    census_eins19
    census_eins20
    census_eins21
    census_eins22
    census_findings16
    census_findings17
    census_findings18
    census_findings19
    census_findings20
    census_findings21
    census_findings22
    census_findingstext19
    census_findingstext20
    census_findingstext21
    census_findingstext22
    census_findingstext_formatted19
    census_findingstext_formatted20
    census_findingstext_formatted21
    census_findingstext_formatted22
    census_gen16
    census_gen17
    census_gen18
    census_gen19
    census_gen20
    census_gen21
    census_gen22
    census_notes19
    census_notes20
    census_notes21
    census_notes22
    census_passthrough16
    census_passthrough17
    census_passthrough18
    census_passthrough19
    census_passthrough20
    census_passthrough21
    census_passthrough22
    census_revisions19
    census_revisions20
    census_revisions21
    census_revisions22
    census_ueis22))

(define (just-table-names lot)
  (define tables (make-hash))
  (for ([t lot])
    (define m (regexp-match "([a-z_]+)([0-9]+)" (~a t)))
    (define key (second m))
    (define v (third m))
    (hash-set! tables
               key
              (cons v (hash-ref tables key '()))
              ))
  tables)

(define (generate-views lot)
  (printf "begin;~n~n")
  (for ([t lot])
    (define clean (regexp-replace "census_" (~a t) ""))
    (printf "create view ~a.~a as~n" schema clean)
    (printf "\tselect *~n")
    (printf "\tfrom ~a~n" t)
    (printf "\torder by ~a.id~n" t)
    (printf ";\n\n"))
  (printf "commit;~n")
  (printf "notify pgrst, 'reload schema';~n"))

(define (generate-drops lot)
  (printf "begin;~n~n")
  (for ([t lot])
    (printf "drop table if exists ~a.~a;~n" schema t))
  (printf "commit;~n")
  (printf "notify pgrst, 'reload schema';~n"))
