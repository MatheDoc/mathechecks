-- One-time backfill: recalculate available_from for currently due/blocked
-- check steps that were set with an uncapped (too large) G-gap.
--
-- After the cap fix in 20260624120000, get_session_core_gap_interval now
-- returns the correct (shorter) gap for sessions with tight deadlines.
-- This migration updates already-stored available_from values so they
-- reflect the corrected gap rather than the old oversized one.
--
-- Safety: we only lower available_from, never raise it.
-- We only touch rows where last_completed_at is set (gap-based timing).

update public.session_check_state scs
set    available_from = scs.last_completed_at
                        + public.get_session_core_gap_interval(scs.session_id)
from   public.learning_sessions ls
where  scs.session_id = ls.id
  and  scs.last_completed_at is not null
  and  scs.available_from    is not null
  and  scs.current_step_status in ('due', 'blocked')
  -- only when the stored available_from exceeds the end of the target day
  and  ls.target_date is not null
  and  ls.target_source = 'explicit'
  and  scs.available_from > (ls.target_date + 1)::timestamp
  -- safety: only shorten, never extend
  and  scs.last_completed_at + public.get_session_core_gap_interval(scs.session_id)
       < scs.available_from;
