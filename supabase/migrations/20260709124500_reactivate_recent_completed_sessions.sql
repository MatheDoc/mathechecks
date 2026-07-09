-- One-time repair for sessions completed during the short interval where the
-- final Kompetenzlisten gate still marked the learning session as completed.
-- Keep this intentionally narrow: only recent fully completed sessions without
-- another active session for the same user are reactivated.

with repair_candidates as (
    select ls.id
    from public.learning_sessions ls
    where ls.status = 'completed'
      and ls.ended_at >= now() - interval '6 hours'
      and not exists (
          select 1
          from public.learning_sessions active_ls
          where active_ls.user_id = ls.user_id
            and active_ls.status = 'active'
      )
      and exists (
          select 1
          from public.session_check_state scs
          where scs.session_id = ls.id
      )
      and not exists (
          select 1
          from public.session_check_state scs
          where scs.session_id = ls.id
            and scs.current_step_key <> 'check_completed'
      )
)
update public.learning_sessions ls
set status = 'active',
    ended_at = null
from repair_candidates
where ls.id = repair_candidates.id;