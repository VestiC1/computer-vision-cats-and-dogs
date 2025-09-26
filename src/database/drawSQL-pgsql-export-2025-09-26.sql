CREATE TABLE "feedback"(
    "id" INTEGER NOT NULL,
    "feed_back_value" INTEGER NOT NULL,
    "prob_cat" FLOAT(53) NOT NULL,
    "prob_dog" FLOAT(53) NOT NULL,
    "last_modified" TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL
);
ALTER TABLE
    "feedback" ADD PRIMARY KEY("id");
CREATE TABLE "monitoring"(
    "id" INTEGER NOT NULL,
    "feedback_id" INTEGER NOT NULL,
    "timestamp" TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
    "inference_time" FLOAT(53) NOT NULL,
    "succes" BOOLEAN NOT NULL
);
ALTER TABLE
    "monitoring" ADD PRIMARY KEY("id");
ALTER TABLE
    "monitoring" ADD CONSTRAINT "monitoring_feedback_id_foreign" FOREIGN KEY("feedback_id") REFERENCES "feedback"("id");