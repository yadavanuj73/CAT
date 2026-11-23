-- ==========================================================================
-- CAT Intelligence 2026 — Row Level Security policies
-- ==========================================================================
-- Apply after running the initial migration.  Designed for Supabase where
-- `auth.uid()` returns the authenticated user's UUID and the `service_role`
-- key bypasses RLS automatically.
--
-- Usage:
--   psql -f rls_policies.sql
-- ==========================================================================

-- ── Helper: list of all user-scoped tables and their user FK column ──
-- (Tables without a direct user_id are covered by cascading through the
--  parent table's RLS or by service-role-only access.)

-- =========================================================================
-- 1. users
-- =========================================================================
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE users FORCE ROW LEVEL SECURITY;

CREATE POLICY users_select ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY users_insert ON users
    FOR INSERT WITH CHECK (auth.uid() = id);

CREATE POLICY users_update ON users
    FOR UPDATE USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

CREATE POLICY users_delete ON users
    FOR DELETE USING (auth.uid() = id);

-- Service-role bypass (Supabase service_role key skips RLS by default;
-- this explicit policy makes it visible in pg_policies).
CREATE POLICY users_service_bypass ON users
    FOR ALL
    USING (current_setting('request.jwt.claim.role', true) = 'service_role');

-- =========================================================================
-- 2. user_settings
-- =========================================================================
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_settings FORCE ROW LEVEL SECURITY;

CREATE POLICY user_settings_select ON user_settings
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY user_settings_insert ON user_settings
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY user_settings_update ON user_settings
    FOR UPDATE USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY user_settings_delete ON user_settings
    FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY user_settings_service_bypass ON user_settings
    FOR ALL
    USING (current_setting('request.jwt.claim.role', true) = 'service_role');

-- =========================================================================
-- 3. encrypted_credentials
-- =========================================================================
ALTER TABLE encrypted_credentials ENABLE ROW LEVEL SECURITY;
ALTER TABLE encrypted_credentials FORCE ROW LEVEL SECURITY;

CREATE POLICY encrypted_credentials_select ON encrypted_credentials
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY encrypted_credentials_insert ON encrypted_credentials
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY encrypted_credentials_update ON encrypted_credentials
    FOR UPDATE USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY encrypted_credentials_delete ON encrypted_credentials
    FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY encrypted_credentials_service_bypass ON encrypted_credentials
    FOR ALL
    USING (current_setting('request.jwt.claim.role', true) = 'service_role');

-- =========================================================================
-- 4. papers
-- =========================================================================
ALTER TABLE papers ENABLE ROW LEVEL SECURITY;
ALTER TABLE papers FORCE ROW LEVEL SECURITY;

CREATE POLICY papers_select ON papers
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY papers_insert ON papers
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY papers_update ON papers
    FOR UPDATE USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY papers_delete ON papers
    FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY papers_service_bypass ON papers
    FOR ALL
    USING (current_setting('request.jwt.claim.role', true) = 'service_role');

-- =========================================================================
-- 5. paper_sources  (user_id resolved through papers FK)
-- =========================================================================
ALTER TABLE paper_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE paper_sources FORCE ROW LEVEL SECURITY;

CREATE POLICY paper_sources_select ON paper_sources
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM papers WHERE papers.id = paper_sources.paper_id
            AND papers.user_id = auth.uid()
        )
    );

CREATE POLICY paper_sources_insert ON paper_sources
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM papers WHERE papers.id = paper_sources.paper_id
            AND papers.user_id = auth.uid()
        )
    );

CREATE POLICY paper_sources_update ON paper_sources
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM papers WHERE papers.id = paper_sources.paper_id
            AND papers.user_id = auth.uid()
        )
    );

CREATE POLICY paper_sources_delete ON paper_sources
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM papers WHERE papers.id = paper_sources.paper_id
            AND papers.user_id = auth.uid()
        )
    );

CREATE POLICY paper_sources_service_bypass ON paper_sources
    FOR ALL
    USING (current_setting('request.jwt.claim.role', true) = 'service_role');

-- =========================================================================
-- 6. questions
-- =========================================================================
ALTER TABLE questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE questions FORCE ROW LEVEL SECURITY;

CREATE POLICY questions_select ON questions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY questions_insert ON questions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY questions_update ON questions
    FOR UPDATE USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY questions_delete ON questions
    FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY questions_service_bypass ON questions
    FOR ALL
    USING (current_setting('request.jwt.claim.role', true) = 'service_role');

-- =========================================================================
-- 7. question_options  (user_id resolved through questions FK)
-- =========================================================================
ALTER TABLE question_options ENABLE ROW LEVEL SECURITY;
ALTER TABLE question_options FORCE ROW LEVEL SECURITY;

CREATE POLICY question_options_select ON question_options
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM questions WHERE questions.id = question_options.question_id
            AND questions.user_id = auth.uid()
        )
    );

CREATE POLICY question_options_insert ON question_options
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM questions WHERE questions.id = question_options.question_id
            AND questions.user_id = auth.uid()
        )
    );

CREATE POLICY question_options_update ON question_options
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM questions WHERE questions.id = question_options.question_id
            AND questions.user_id = auth.uid()
        )
    );

CREATE POLICY question_options_delete ON question_options
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM questions WHERE questions.id = question_options.question_id
            AND questions.user_id = auth.uid()
        )
    );

CREATE POLICY question_options_service_bypass ON question_options
    FOR ALL
    USING (current_setting('request.jwt.claim.role', true) = 'service_role');

-- =========================================================================
-- 8. answer_keys  (user_id resolved through questions FK)
-- =========================================================================
ALTER TABLE answer_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE answer_keys FORCE ROW LEVEL SECURITY;

CREATE POLICY answer_keys_select ON answer_keys
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM questions WHERE questions.id = answer_keys.question_id
            AND questions.user_id = auth.uid()
        )
    );

CREATE POLICY answer_keys_insert ON answer_keys
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM questions WHERE questions.id = answer_keys.question_id
            AND questions.user_id = auth.uid()
        )
    );

CREATE POLICY answer_keys_update ON answer_keys
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM questions WHERE questions.id = answer_keys.question_id
            AND questions.user_id = auth.uid()
        )
    );

CREATE POLICY answer_keys_delete ON answer_keys
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM questions WHERE questions.id = answer_keys.question_id
            AND questions.user_id = auth.uid()
        )
    );

CREATE POLICY answer_keys_service_bypass ON answer_keys
    FOR ALL
    USING (current_setting('request.jwt.claim.role', true) = 'service_role');

-- =========================================================================
-- 9. solutions  (user_id resolved through questions FK)
-- =========================================================================
ALTER TABLE solutions ENABLE ROW LEVEL SECURITY;
ALTER TABLE solutions FORCE ROW LEVEL SECURITY;

CREATE POLICY solutions_select ON solutions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM questions WHERE questions.id = solutions.question_id
            AND questions.user_id = auth.uid()
        )
    );

CREATE POLICY solutions_insert ON solutions
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM questions WHERE questions.id = solutions.question_id
            AND questions.user_id = auth.uid()
        )
    );

CREATE POLICY solutions_update ON solutions
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM questions WHERE questions.id = solutions.question_id
            AND questions.user_id = auth.uid()
        )
    );

CREATE POLICY solutions_delete ON solutions
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM questions WHERE questions.id = solutions.question_id
            AND questions.user_id = auth.uid()
        )
    );

CREATE POLICY solutions_service_bypass ON solutions
    FOR ALL
    USING (current_setting('request.jwt.claim.role', true) = 'service_role');

-- =========================================================================
-- 10. topics  (shared reference data — read-only for users, writable by service)
-- =========================================================================
ALTER TABLE topics ENABLE ROW LEVEL SECURITY;
ALTER TABLE topics FORCE ROW LEVEL SECURITY;

CREATE POLICY topics_select ON topics
    FOR SELECT USING (true);  -- all authenticated users can read topics

CREATE POLICY topics_service_bypass ON topics
    FOR ALL
    USING (current_setting('request.jwt.claim.role', true) = 'service_role');

-- =========================================================================
-- 11. question_classifications  (user_id resolved through questions FK)
-- =========================================================================
ALTER TABLE question_classifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE question_classifications FORCE ROW LEVEL SECURITY;

CREATE POLICY question_classifications_select ON question_classifications
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM questions WHERE questions.id = question_classifications.question_id
            AND questions.user_id = auth.uid()
        )
    );

CREATE POLICY question_classifications_insert ON question_classifications
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM questions WHERE questions.id = question_classifications.question_id
            AND questions.user_id = auth.uid()
        )
    );

CREATE POLICY question_classifications_update ON question_classifications
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM questions WHERE questions.id = question_classifications.question_id
            AND questions.user_id = auth.uid()
        )
    );

CREATE POLICY question_classifications_delete ON question_classifications
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM questions WHERE questions.id = question_classifications.question_id
            AND questions.user_id = auth.uid()
        )
    );

CREATE POLICY question_classifications_service_bypass ON question_classifications
    FOR ALL
    USING (current_setting('request.jwt.claim.role', true) = 'service_role');

-- =========================================================================
-- 12. analysis_results
-- =========================================================================
ALTER TABLE analysis_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE analysis_results FORCE ROW LEVEL SECURITY;

CREATE POLICY analysis_results_select ON analysis_results
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY analysis_results_insert ON analysis_results
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY analysis_results_update ON analysis_results
    FOR UPDATE USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY analysis_results_delete ON analysis_results
    FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY analysis_results_service_bypass ON analysis_results
    FOR ALL
    USING (current_setting('request.jwt.claim.role', true) = 'service_role');

-- =========================================================================
-- 13. predictions
-- =========================================================================
ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE predictions FORCE ROW LEVEL SECURITY;

CREATE POLICY predictions_select ON predictions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY predictions_insert ON predictions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY predictions_update ON predictions
    FOR UPDATE USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY predictions_delete ON predictions
    FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY predictions_service_bypass ON predictions
    FOR ALL
    USING (current_setting('request.jwt.claim.role', true) = 'service_role');

-- =========================================================================
-- 14. prediction_evidence  (user_id resolved through predictions FK)
-- =========================================================================
ALTER TABLE prediction_evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE prediction_evidence FORCE ROW LEVEL SECURITY;

CREATE POLICY prediction_evidence_select ON prediction_evidence
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM predictions WHERE predictions.id = prediction_evidence.prediction_id
            AND predictions.user_id = auth.uid()
        )
    );

CREATE POLICY prediction_evidence_insert ON prediction_evidence
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM predictions WHERE predictions.id = prediction_evidence.prediction_id
            AND predictions.user_id = auth.uid()
        )
    );

CREATE POLICY prediction_evidence_update ON prediction_evidence
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM predictions WHERE predictions.id = prediction_evidence.prediction_id
            AND predictions.user_id = auth.uid()
        )
    );

CREATE POLICY prediction_evidence_delete ON prediction_evidence
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM predictions WHERE predictions.id = prediction_evidence.prediction_id
            AND predictions.user_id = auth.uid()
        )
    );

CREATE POLICY prediction_evidence_service_bypass ON prediction_evidence
    FOR ALL
    USING (current_setting('request.jwt.claim.role', true) = 'service_role');

-- =========================================================================
-- 15. mock_exams
-- =========================================================================
ALTER TABLE mock_exams ENABLE ROW LEVEL SECURITY;
ALTER TABLE mock_exams FORCE ROW LEVEL SECURITY;

CREATE POLICY mock_exams_select ON mock_exams
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY mock_exams_insert ON mock_exams
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY mock_exams_update ON mock_exams
    FOR UPDATE USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY mock_exams_delete ON mock_exams
    FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY mock_exams_service_bypass ON mock_exams
    FOR ALL
    USING (current_setting('request.jwt.claim.role', true) = 'service_role');

-- =========================================================================
-- 16. mock_questions  (user_id resolved through mock_exams FK)
-- =========================================================================
ALTER TABLE mock_questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE mock_questions FORCE ROW LEVEL SECURITY;

CREATE POLICY mock_questions_select ON mock_questions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM mock_exams WHERE mock_exams.id = mock_questions.mock_exam_id
            AND mock_exams.user_id = auth.uid()
        )
    );

CREATE POLICY mock_questions_insert ON mock_questions
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM mock_exams WHERE mock_exams.id = mock_questions.mock_exam_id
            AND mock_exams.user_id = auth.uid()
        )
    );

CREATE POLICY mock_questions_update ON mock_questions
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM mock_exams WHERE mock_exams.id = mock_questions.mock_exam_id
            AND mock_exams.user_id = auth.uid()
        )
    );

CREATE POLICY mock_questions_delete ON mock_questions
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM mock_exams WHERE mock_exams.id = mock_questions.mock_exam_id
            AND mock_exams.user_id = auth.uid()
        )
    );

CREATE POLICY mock_questions_service_bypass ON mock_questions
    FOR ALL
    USING (current_setting('request.jwt.claim.role', true) = 'service_role');

-- =========================================================================
-- 17. exam_attempts
-- =========================================================================
ALTER TABLE exam_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE exam_attempts FORCE ROW LEVEL SECURITY;

CREATE POLICY exam_attempts_select ON exam_attempts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY exam_attempts_insert ON exam_attempts
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY exam_attempts_update ON exam_attempts
    FOR UPDATE USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY exam_attempts_delete ON exam_attempts
    FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY exam_attempts_service_bypass ON exam_attempts
    FOR ALL
    USING (current_setting('request.jwt.claim.role', true) = 'service_role');

-- =========================================================================
-- 18. verification_records  (user_id resolved through questions/mock_questions FK)
-- =========================================================================
ALTER TABLE verification_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE verification_records FORCE ROW LEVEL SECURITY;

CREATE POLICY verification_records_select ON verification_records
    FOR SELECT USING (
        (question_id IS NOT NULL AND EXISTS (
            SELECT 1 FROM questions WHERE questions.id = verification_records.question_id
            AND questions.user_id = auth.uid()
        ))
        OR
        (mock_question_id IS NOT NULL AND EXISTS (
            SELECT 1 FROM mock_questions
            JOIN mock_exams ON mock_exams.id = mock_questions.mock_exam_id
            WHERE mock_questions.id = verification_records.mock_question_id
            AND mock_exams.user_id = auth.uid()
        ))
    );

CREATE POLICY verification_records_insert ON verification_records
    FOR INSERT WITH CHECK (
        (question_id IS NOT NULL AND EXISTS (
            SELECT 1 FROM questions WHERE questions.id = verification_records.question_id
            AND questions.user_id = auth.uid()
        ))
        OR
        (mock_question_id IS NOT NULL AND EXISTS (
            SELECT 1 FROM mock_questions
            JOIN mock_exams ON mock_exams.id = mock_questions.mock_exam_id
            WHERE mock_questions.id = verification_records.mock_question_id
            AND mock_exams.user_id = auth.uid()
        ))
    );

CREATE POLICY verification_records_update ON verification_records
    FOR UPDATE USING (
        (question_id IS NOT NULL AND EXISTS (
            SELECT 1 FROM questions WHERE questions.id = verification_records.question_id
            AND questions.user_id = auth.uid()
        ))
        OR
        (mock_question_id IS NOT NULL AND EXISTS (
            SELECT 1 FROM mock_questions
            JOIN mock_exams ON mock_exams.id = mock_questions.mock_exam_id
            WHERE mock_questions.id = verification_records.mock_question_id
            AND mock_exams.user_id = auth.uid()
        ))
    );

CREATE POLICY verification_records_delete ON verification_records
    FOR DELETE USING (
        (question_id IS NOT NULL AND EXISTS (
            SELECT 1 FROM questions WHERE questions.id = verification_records.question_id
            AND questions.user_id = auth.uid()
        ))
        OR
        (mock_question_id IS NOT NULL AND EXISTS (
            SELECT 1 FROM mock_questions
            JOIN mock_exams ON mock_exams.id = mock_questions.mock_exam_id
            WHERE mock_questions.id = verification_records.mock_question_id
            AND mock_exams.user_id = auth.uid()
        ))
    );

CREATE POLICY verification_records_service_bypass ON verification_records
    FOR ALL
    USING (current_setting('request.jwt.claim.role', true) = 'service_role');

-- =========================================================================
-- 19. audit_logs
-- =========================================================================
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs FORCE ROW LEVEL SECURITY;

CREATE POLICY audit_logs_select ON audit_logs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY audit_logs_insert ON audit_logs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Audit logs are append-only: no UPDATE or DELETE for users.
-- Service role can still manage them.

CREATE POLICY audit_logs_service_bypass ON audit_logs
    FOR ALL
    USING (current_setting('request.jwt.claim.role', true) = 'service_role');

-- =========================================================================
-- 20. user_upload_permissions
-- =========================================================================
ALTER TABLE user_upload_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_upload_permissions FORCE ROW LEVEL SECURITY;

CREATE POLICY user_upload_permissions_select ON user_upload_permissions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY user_upload_permissions_insert ON user_upload_permissions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY user_upload_permissions_update ON user_upload_permissions
    FOR UPDATE USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY user_upload_permissions_delete ON user_upload_permissions
    FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY user_upload_permissions_service_bypass ON user_upload_permissions
    FOR ALL
    USING (current_setting('request.jwt.claim.role', true) = 'service_role');

-- =========================================================================
-- 21. user_processing_history
-- =========================================================================
ALTER TABLE user_processing_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_processing_history FORCE ROW LEVEL SECURITY;

CREATE POLICY user_processing_history_select ON user_processing_history
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY user_processing_history_insert ON user_processing_history
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY user_processing_history_service_bypass ON user_processing_history
    FOR ALL
    USING (current_setting('request.jwt.claim.role', true) = 'service_role');

-- =========================================================================
-- 22. Shared Question Bank & Analytics (All authenticated users can SELECT)
-- =========================================================================
ALTER TABLE shared_historical_papers ENABLE ROW LEVEL SECURITY;
CREATE POLICY shared_papers_select_all ON shared_historical_papers
    FOR SELECT TO authenticated USING (true);
CREATE POLICY shared_papers_service_all ON shared_historical_papers
    FOR ALL USING (current_setting('request.jwt.claim.role', true) = 'service_role');

ALTER TABLE shared_verified_questions ENABLE ROW LEVEL SECURITY;
CREATE POLICY shared_questions_select_all ON shared_verified_questions
    FOR SELECT TO authenticated USING (true);
CREATE POLICY shared_questions_service_all ON shared_verified_questions
    FOR ALL USING (current_setting('request.jwt.claim.role', true) = 'service_role');

ALTER TABLE shared_question_options ENABLE ROW LEVEL SECURITY;
CREATE POLICY shared_options_select_all ON shared_question_options
    FOR SELECT TO authenticated USING (true);
CREATE POLICY shared_options_service_all ON shared_question_options
    FOR ALL USING (current_setting('request.jwt.claim.role', true) = 'service_role');

ALTER TABLE shared_answer_keys ENABLE ROW LEVEL SECURITY;
CREATE POLICY shared_answer_keys_select_all ON shared_answer_keys
    FOR SELECT TO authenticated USING (true);
CREATE POLICY shared_answer_keys_service_all ON shared_answer_keys
    FOR ALL USING (current_setting('request.jwt.claim.role', true) = 'service_role');

ALTER TABLE shared_solutions ENABLE ROW LEVEL SECURITY;
CREATE POLICY shared_solutions_select_all ON shared_solutions
    FOR SELECT TO authenticated USING (true);
CREATE POLICY shared_solutions_service_all ON shared_solutions
    FOR ALL USING (current_setting('request.jwt.claim.role', true) = 'service_role');

ALTER TABLE shared_question_sources ENABLE ROW LEVEL SECURITY;
CREATE POLICY shared_sources_select_all ON shared_question_sources
    FOR SELECT TO authenticated USING (true);
CREATE POLICY shared_sources_service_all ON shared_question_sources
    FOR ALL USING (current_setting('request.jwt.claim.role', true) = 'service_role');

ALTER TABLE shared_question_topics ENABLE ROW LEVEL SECURITY;
CREATE POLICY shared_topics_select_all ON shared_question_topics
    FOR SELECT TO authenticated USING (true);
CREATE POLICY shared_topics_service_all ON shared_question_topics
    FOR ALL USING (current_setting('request.jwt.claim.role', true) = 'service_role');

ALTER TABLE topic_frequency_statistics ENABLE ROW LEVEL SECURITY;
CREATE POLICY topic_freq_select_all ON topic_frequency_statistics
    FOR SELECT TO authenticated USING (true);
CREATE POLICY topic_freq_service_all ON topic_frequency_statistics
    FOR ALL USING (current_setting('request.jwt.claim.role', true) = 'service_role');

ALTER TABLE yearly_trends ENABLE ROW LEVEL SECURITY;
CREATE POLICY yearly_trends_select_all ON yearly_trends
    FOR SELECT TO authenticated USING (true);
CREATE POLICY yearly_trends_service_all ON yearly_trends
    FOR ALL USING (current_setting('request.jwt.claim.role', true) = 'service_role');

ALTER TABLE difficulty_statistics ENABLE ROW LEVEL SECURITY;
CREATE POLICY diff_stats_select_all ON difficulty_statistics
    FOR SELECT TO authenticated USING (true);
CREATE POLICY diff_stats_service_all ON difficulty_statistics
    FOR ALL USING (current_setting('request.jwt.claim.role', true) = 'service_role');
