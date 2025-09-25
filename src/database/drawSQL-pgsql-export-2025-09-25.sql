CREATE TABLE "Monitoring"(
    "id" INTEGER NOT NULL,
    "timestamp" TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
    "inference_time" FLOAT(53) NOT NULL,
    "succes" BOOLEAN NOT NULL
);
ALTER TABLE
    "Monitoring" ADD PRIMARY KEY("id");
CREATE TABLE "Feedback"(
    "id" INTEGER NOT NULL,
    "feed_back_value" INTEGER NOT NULL,
    "prob_cat" FLOAT(53) NOT NULL,
    "prob_dog" FLOAT(53) NOT NULL,
    "last_modified" TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL
);
ALTER TABLE
    "Feedback" ADD PRIMARY KEY("id");
ALTER TABLE
    "Monitoring" ADD CONSTRAINT "monitoring_id_foreign" FOREIGN KEY("id") REFERENCES "Feedback"("id");