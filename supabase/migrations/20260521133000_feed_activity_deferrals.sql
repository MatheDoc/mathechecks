insert into public.system_settings (setting_key, value_integer, description)
values
    ('feed.deferred_activity_gap', 3, 'Wie viele weitere abgeschlossene Feed-Aktivitäten eine zurückgestellte Aktivität aus dem normalen Feed herausnimmt, bevor sie wieder normal eingemischt wird.')
on conflict (setting_key) do update
set value_integer = excluded.value_integer,
    description = excluded.description;

create table if not exists public.user_feed_activity_deferrals (
    user_id uuid not null references auth.users(id) on delete cascade,
    activity_key text not null,
    defer_until_activity_count bigint not null check (defer_until_activity_count >= 0),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    primary key (user_id, activity_key),
    check (char_length(trim(activity_key)) > 0)
);

create index if not exists user_feed_activity_deferrals_due_idx
    on public.user_feed_activity_deferrals (user_id, defer_until_activity_count, activity_key);

drop trigger if exists set_user_feed_activity_deferrals_updated_at on public.user_feed_activity_deferrals;
create trigger set_user_feed_activity_deferrals_updated_at
    before update on public.user_feed_activity_deferrals
    for each row execute function public.set_updated_at();

grant select on public.user_feed_activity_deferrals to authenticated;

alter table public.user_feed_activity_deferrals enable row level security;

drop policy if exists user_feed_activity_deferrals_select_own on public.user_feed_activity_deferrals;
create policy user_feed_activity_deferrals_select_own
    on public.user_feed_activity_deferrals
    for select
    to authenticated
    using (user_id = auth.uid());

create or replace function public.defer_feed_activity(
    p_activity_key text
)
returns bigint
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    normalized_activity_key text := nullif(trim(p_activity_key), '');
    current_completed_activity_count bigint := public.get_current_feed_activity_completion_count();
    deferred_activity_gap integer := greatest(public.get_system_setting_integer('feed.deferred_activity_gap', 3), 1);
    deferred_until_activity_count bigint := current_completed_activity_count + deferred_activity_gap;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if normalized_activity_key is null then
        raise exception 'activity_key is required';
    end if;

    insert into public.user_feed_activity_deferrals (
        user_id,
        activity_key,
        defer_until_activity_count
    )
    values (
        current_user_id,
        normalized_activity_key,
        deferred_until_activity_count
    )
    on conflict (user_id, activity_key) do update
    set defer_until_activity_count = excluded.defer_until_activity_count;

    return deferred_until_activity_count;
end;
$$;

create or replace function public.clear_feed_activity_deferral(
    p_activity_key text
)
returns void
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    normalized_activity_key text := nullif(trim(p_activity_key), '');
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if normalized_activity_key is null then
        return;
    end if;

    delete from public.user_feed_activity_deferrals
    where user_id = current_user_id
      and activity_key = normalized_activity_key;
end;
$$;

revoke all on function public.defer_feed_activity(text) from public;
revoke all on function public.defer_feed_activity(text) from anon;
grant execute on function public.defer_feed_activity(text) to authenticated;

revoke all on function public.clear_feed_activity_deferral(text) from public;
revoke all on function public.clear_feed_activity_deferral(text) from anon;
grant execute on function public.clear_feed_activity_deferral(text) to authenticated;