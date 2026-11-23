CREATE TABLE difficulty_statistics (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	section VARCHAR(16) NOT NULL, 
	difficulty VARCHAR(16) NOT NULL, 
	count INTEGER NOT NULL, 
	percentage FLOAT NOT NULL, 
	last_calculated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_diff_stat_section_diff UNIQUE (section, difficulty)
);

CREATE TABLE duplicate_detection_records (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	entity_type VARCHAR(32) NOT NULL, 
	source_id UUID NOT NULL, 
	target_id UUID, 
	detection_level VARCHAR(32) NOT NULL, 
	similarity_score FLOAT NOT NULL, 
	match_metadata JSONB, 
	action_taken VARCHAR(32) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE review_queue (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	entity_type VARCHAR(32) NOT NULL, 
	entity_id UUID NOT NULL, 
	reason TEXT NOT NULL, 
	severity VARCHAR(16) NOT NULL, 
	status VARCHAR(32) NOT NULL, 
	assigned_to VARCHAR(128), 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE shared_historical_papers (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	year INTEGER NOT NULL, 
	slot VARCHAR(32), 
	paper_title VARCHAR(256) NOT NULL, 
	file_fingerprint VARCHAR(64) NOT NULL, 
	total_questions INTEGER NOT NULL, 
	is_verified BOOLEAN DEFAULT 'true' NOT NULL, 
	source_provenance VARCHAR(256), 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_shared_papers_year_range CHECK (year >= 2000 AND year <= 2025), 
	CONSTRAINT uq_shared_papers_year_slot UNIQUE (year, slot)
);

CREATE TABLE topic_frequency_statistics (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	section VARCHAR(16) NOT NULL, 
	topic VARCHAR(128) NOT NULL, 
	subtopic VARCHAR(128), 
	total_occurrences INTEGER NOT NULL, 
	recent_occurrences INTEGER NOT NULL, 
	frequency_score FLOAT NOT NULL, 
	recency_weighted_score FLOAT NOT NULL, 
	last_calculated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_topic_freq_sec_topic_sub UNIQUE (section, topic, subtopic)
);

CREATE TABLE topics (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	section section NOT NULL, 
	topic_name VARCHAR(256) NOT NULL, 
	subtopic_name VARCHAR(256), 
	description TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_topics_section_topic_subtopic UNIQUE (section, topic_name, subtopic_name)
);

CREATE TABLE users (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	email VARCHAR(320) NOT NULL, 
	password_hash VARCHAR(256) NOT NULL, 
	is_active BOOLEAN DEFAULT 'true' NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE yearly_trends (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	year INTEGER NOT NULL, 
	section VARCHAR(16) NOT NULL, 
	total_questions INTEGER NOT NULL, 
	mcq_count INTEGER NOT NULL, 
	tita_count INTEGER NOT NULL, 
	easy_count INTEGER NOT NULL, 
	medium_count INTEGER NOT NULL, 
	hard_count INTEGER NOT NULL, 
	last_calculated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_yearly_trend_year_section UNIQUE (year, section)
);

CREATE TABLE analysis_results (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	user_id UUID NOT NULL, 
	section section NOT NULL, 
	analysis_type VARCHAR(128) NOT NULL, 
	parameters JSONB, 
	result_data JSONB NOT NULL, 
	methodology TEXT, 
	data_coverage JSONB, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE audit_logs (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	user_id UUID NOT NULL, 
	action VARCHAR(256) NOT NULL, 
	entity_type VARCHAR(128), 
	entity_id UUID, 
	details JSONB, 
	ip_address VARCHAR(45), 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE encrypted_credentials (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	user_id UUID NOT NULL, 
	provider VARCHAR(64) NOT NULL, 
	encrypted_key BYTEA NOT NULL, 
	iv BYTEA NOT NULL, 
	auth_tag BYTEA NOT NULL, 
	key_version INTEGER NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE mock_exams (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	user_id UUID NOT NULL, 
	exam_type exam_type NOT NULL, 
	title VARCHAR(512) NOT NULL, 
	description TEXT, 
	section section, 
	topic_id UUID, 
	total_questions INTEGER NOT NULL, 
	total_marks FLOAT NOT NULL, 
	duration_minutes INTEGER NOT NULL, 
	marking_scheme JSONB, 
	verification_status mock_verification_status DEFAULT 'pending' NOT NULL, 
	questions_verified INTEGER DEFAULT '0' NOT NULL, 
	questions_failed INTEGER DEFAULT '0' NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(topic_id) REFERENCES topics (id) ON DELETE SET NULL
);

CREATE TABLE paper_fingerprints (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	file_hash VARCHAR(64) NOT NULL, 
	shared_paper_id UUID, 
	first_seen_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	times_seen INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(shared_paper_id) REFERENCES shared_historical_papers (id) ON DELETE SET NULL
);

CREATE TABLE papers (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	user_id UUID NOT NULL, 
	year INTEGER NOT NULL, 
	slot VARCHAR(32), 
	source_name VARCHAR(256), 
	original_filename VARCHAR(512), 
	file_path VARCHAR(1024), 
	file_hash VARCHAR(64), 
	status paper_status DEFAULT 'uploaded' NOT NULL, 
	extraction_confidence FLOAT, 
	total_questions INTEGER, 
	notes TEXT, 
	allow_sharing BOOLEAN DEFAULT 'true' NOT NULL, 
	sharing_status VARCHAR(32) DEFAULT 'pending' NOT NULL, 
	error_details TEXT, 
	is_duplicate BOOLEAN DEFAULT 'false' NOT NULL, 
	duplicate_of_id UUID, 
	shared_paper_id UUID, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_papers_year_range CHECK (year >= 2000 AND year <= 2025), 
	CONSTRAINT ck_papers_extraction_confidence_range CHECK (extraction_confidence IS NULL OR (extraction_confidence >= 0 AND extraction_confidence <= 1)), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(shared_paper_id) REFERENCES shared_historical_papers (id) ON DELETE SET NULL
);

CREATE TABLE predictions (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	user_id UUID NOT NULL, 
	section section NOT NULL, 
	topic_id UUID NOT NULL, 
	predicted_archetype VARCHAR(256), 
	statistical_score FLOAT, 
	confidence FLOAT, 
	explanation TEXT, 
	limitations TEXT, 
	methodology TEXT, 
	backtesting_score FLOAT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_predictions_statistical_score_range CHECK (statistical_score IS NULL OR (statistical_score >= 0 AND statistical_score <= 1)), 
	CONSTRAINT ck_predictions_confidence_range CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 1)), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(topic_id) REFERENCES topics (id) ON DELETE SET NULL
);

CREATE TABLE shared_verified_questions (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	shared_paper_id UUID, 
	canonical_hash VARCHAR(64) NOT NULL, 
	question_number INTEGER NOT NULL, 
	question_text TEXT NOT NULL, 
	canonical_text TEXT NOT NULL, 
	question_type question_type NOT NULL, 
	section section NOT NULL, 
	difficulty difficulty NOT NULL, 
	marks_positive FLOAT NOT NULL, 
	marks_negative FLOAT NOT NULL, 
	has_image BOOLEAN DEFAULT 'false' NOT NULL, 
	has_table BOOLEAN DEFAULT 'false' NOT NULL, 
	has_passage BOOLEAN DEFAULT 'false' NOT NULL, 
	passage_text TEXT, 
	dataset_text TEXT, 
	primary_year INTEGER NOT NULL, 
	primary_slot VARCHAR(32), 
	verification_status VARCHAR(32) NOT NULL, 
	verification_confidence FLOAT NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_shared_q_year_range CHECK (primary_year >= 2000 AND primary_year <= 2025), 
	FOREIGN KEY(shared_paper_id) REFERENCES shared_historical_papers (id) ON DELETE SET NULL
);

CREATE TABLE user_settings (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	user_id UUID NOT NULL, 
	setting_key VARCHAR(128) NOT NULL, 
	setting_value TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE exam_attempts (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	user_id UUID NOT NULL, 
	mock_exam_id UUID NOT NULL, 
	started_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	finished_at TIMESTAMP WITH TIME ZONE, 
	time_spent_seconds INTEGER, 
	responses JSONB, 
	score FLOAT, 
	max_score FLOAT NOT NULL, 
	section_scores JSONB, 
	status attempt_status DEFAULT 'in_progress' NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(mock_exam_id) REFERENCES mock_exams (id) ON DELETE CASCADE
);

CREATE TABLE mock_questions (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	mock_exam_id UUID NOT NULL, 
	question_number INTEGER NOT NULL, 
	question_text TEXT NOT NULL, 
	question_type question_type NOT NULL, 
	options JSONB, 
	correct_answer TEXT NOT NULL, 
	solution_text TEXT, 
	topic VARCHAR(256), 
	subtopic VARCHAR(256), 
	difficulty difficulty, 
	estimated_time_seconds INTEGER, 
	marks_positive FLOAT NOT NULL, 
	marks_negative FLOAT NOT NULL, 
	verification_status mock_verification_status DEFAULT 'pending' NOT NULL, 
	verification_details JSONB, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(mock_exam_id) REFERENCES mock_exams (id) ON DELETE CASCADE
);

CREATE TABLE paper_sources (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	paper_id UUID NOT NULL, 
	source_type source_type NOT NULL, 
	source_url VARCHAR(2048), 
	publisher VARCHAR(256), 
	is_verified BOOLEAN DEFAULT 'false' NOT NULL, 
	verification_notes TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(paper_id) REFERENCES papers (id) ON DELETE CASCADE
);

CREATE TABLE question_fingerprints (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	canonical_hash VARCHAR(64) NOT NULL, 
	shared_question_id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(shared_question_id) REFERENCES shared_verified_questions (id) ON DELETE CASCADE
);

CREATE TABLE question_similarity_reviews (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	candidate_question_id UUID NOT NULL, 
	existing_shared_question_id UUID, 
	similarity_score FLOAT NOT NULL, 
	reason TEXT NOT NULL, 
	status VARCHAR(32) NOT NULL, 
	reviewed_by VARCHAR(128), 
	review_notes TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(existing_shared_question_id) REFERENCES shared_verified_questions (id) ON DELETE CASCADE
);

CREATE TABLE questions (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	paper_id UUID NOT NULL, 
	user_id UUID NOT NULL, 
	question_number INTEGER NOT NULL, 
	question_text TEXT NOT NULL, 
	question_type question_type NOT NULL, 
	section section NOT NULL, 
	difficulty difficulty, 
	marks_positive FLOAT NOT NULL, 
	marks_negative FLOAT NOT NULL, 
	has_image BOOLEAN DEFAULT 'false' NOT NULL, 
	has_table BOOLEAN DEFAULT 'false' NOT NULL, 
	has_passage BOOLEAN DEFAULT 'false' NOT NULL, 
	passage_text TEXT, 
	extraction_confidence FLOAT, 
	verification_status verification_status DEFAULT 'unverified' NOT NULL, 
	year INTEGER NOT NULL, 
	slot VARCHAR(32), 
	canonical_hash VARCHAR(64), 
	shared_question_id UUID, 
	rejection_reason TEXT, 
	dataset_text TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_questions_extraction_confidence_range CHECK (extraction_confidence IS NULL OR (extraction_confidence >= 0 AND extraction_confidence <= 1)), 
	FOREIGN KEY(paper_id) REFERENCES papers (id) ON DELETE CASCADE, 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(shared_question_id) REFERENCES shared_verified_questions (id) ON DELETE SET NULL
);

CREATE TABLE shared_answer_keys (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	shared_question_id UUID NOT NULL, 
	correct_answer TEXT NOT NULL, 
	answer_type VARCHAR(16) NOT NULL, 
	provenance TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (shared_question_id), 
	FOREIGN KEY(shared_question_id) REFERENCES shared_verified_questions (id) ON DELETE CASCADE
);

CREATE TABLE shared_question_options (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	shared_question_id UUID NOT NULL, 
	option_label VARCHAR(1) NOT NULL, 
	option_text TEXT NOT NULL, 
	is_correct BOOLEAN DEFAULT 'false' NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_shared_option_question_label UNIQUE (shared_question_id, option_label), 
	FOREIGN KEY(shared_question_id) REFERENCES shared_verified_questions (id) ON DELETE CASCADE
);

CREATE TABLE shared_question_sources (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	shared_question_id UUID NOT NULL, 
	shared_paper_id UUID, 
	year INTEGER NOT NULL, 
	slot VARCHAR(32), 
	question_number INTEGER, 
	source_name VARCHAR(256), 
	source_type VARCHAR(64) NOT NULL, 
	provenance_notes TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_shared_question_source_instance UNIQUE (shared_question_id, year, slot, question_number), 
	FOREIGN KEY(shared_question_id) REFERENCES shared_verified_questions (id) ON DELETE CASCADE, 
	FOREIGN KEY(shared_paper_id) REFERENCES shared_historical_papers (id) ON DELETE SET NULL
);

CREATE TABLE shared_question_topics (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	shared_question_id UUID NOT NULL, 
	topic_id UUID NOT NULL, 
	confidence FLOAT NOT NULL, 
	classified_by VARCHAR(32) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_shared_question_topic UNIQUE (shared_question_id, topic_id), 
	FOREIGN KEY(shared_question_id) REFERENCES shared_verified_questions (id) ON DELETE CASCADE, 
	FOREIGN KEY(topic_id) REFERENCES topics (id) ON DELETE CASCADE
);

CREATE TABLE shared_solutions (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	shared_question_id UUID NOT NULL, 
	solution_text TEXT NOT NULL, 
	approach_type VARCHAR(64), 
	is_verified BOOLEAN DEFAULT 'true' NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (shared_question_id), 
	FOREIGN KEY(shared_question_id) REFERENCES shared_verified_questions (id) ON DELETE CASCADE
);

CREATE TABLE user_processing_history (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	user_id UUID NOT NULL, 
	paper_id UUID NOT NULL, 
	stage VARCHAR(64) NOT NULL, 
	status VARCHAR(32) NOT NULL, 
	details JSONB, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(paper_id) REFERENCES papers (id) ON DELETE CASCADE
);

CREATE TABLE user_upload_permissions (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	user_id UUID NOT NULL, 
	paper_id UUID NOT NULL, 
	allow_sharing BOOLEAN NOT NULL, 
	terms_accepted BOOLEAN NOT NULL, 
	legal_eligibility_confirmed BOOLEAN NOT NULL, 
	granted_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(paper_id) REFERENCES papers (id) ON DELETE CASCADE
);

CREATE TABLE answer_keys (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	question_id UUID NOT NULL, 
	correct_answer TEXT NOT NULL, 
	answer_source TEXT, 
	is_verified BOOLEAN DEFAULT 'false' NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(question_id) REFERENCES questions (id) ON DELETE CASCADE
);

CREATE TABLE prediction_evidence (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	prediction_id UUID NOT NULL, 
	question_id UUID, 
	analysis_id UUID, 
	evidence_type VARCHAR(128) NOT NULL, 
	evidence_text TEXT, 
	weight FLOAT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(prediction_id) REFERENCES predictions (id) ON DELETE CASCADE, 
	FOREIGN KEY(question_id) REFERENCES questions (id) ON DELETE SET NULL, 
	FOREIGN KEY(analysis_id) REFERENCES analysis_results (id) ON DELETE SET NULL
);

CREATE TABLE question_classifications (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	question_id UUID NOT NULL, 
	topic_id UUID NOT NULL, 
	archetype VARCHAR(256), 
	concept_tags TEXT[], 
	confidence FLOAT, 
	classified_by classified_by NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_question_classifications_confidence_range CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 1)), 
	FOREIGN KEY(question_id) REFERENCES questions (id) ON DELETE CASCADE, 
	FOREIGN KEY(topic_id) REFERENCES topics (id) ON DELETE CASCADE
);

CREATE TABLE question_options (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	question_id UUID NOT NULL, 
	option_label VARCHAR(1) NOT NULL, 
	option_text TEXT NOT NULL, 
	is_correct BOOLEAN DEFAULT 'false' NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(question_id) REFERENCES questions (id) ON DELETE CASCADE
);

CREATE TABLE solutions (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	question_id UUID NOT NULL, 
	solution_text TEXT NOT NULL, 
	solution_source TEXT, 
	is_verified BOOLEAN DEFAULT 'false' NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(question_id) REFERENCES questions (id) ON DELETE CASCADE
);

CREATE TABLE verification_records (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	question_id UUID, 
	mock_question_id UUID, 
	verification_type verification_type NOT NULL, 
	result verification_result NOT NULL, 
	details JSONB, 
	verified_by verified_by NOT NULL, 
	verified_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(question_id) REFERENCES questions (id) ON DELETE CASCADE, 
	FOREIGN KEY(mock_question_id) REFERENCES mock_questions (id) ON DELETE CASCADE
);

