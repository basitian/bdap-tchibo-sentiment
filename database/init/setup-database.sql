DROP TABLE IF EXISTS "Reviews";
DROP SEQUENCE IF EXISTS "Reviews_ReviewId_seq";
CREATE SEQUENCE "Reviews_ReviewId_seq";

CREATE TABLE "public"."Reviews" (
    "ProductName" text NOT NULL,
    "ReviewId" integer DEFAULT nextval('"Reviews_ReviewId_seq"') PRIMARY KEY,
    "Rating" integer NOT NULL,
    "SourceReviewId" text,
    "CreatedAt" date NOT NULL,
    "ReviewTitle" text NOT NULL,
    "Source" text NOT NULL,
    "ReviewText" text NOT NULL
) WITH (oids = false);

COPY "Reviews" ("Rating", "ReviewTitle", "ReviewText", "CreatedAt", "ProductName", "Source") FROM '/docker-entrypoint-initdb.d/tchibo_reviews.csv' DELIMITER ',' CSV HEADER;
COPY "Reviews" ("CreatedAt", "ProductName", "Rating", "ReviewText", "ReviewTitle", "Source", "SourceReviewId") FROM '/docker-entrypoint-initdb.d/mediamarkt_reviews.csv' DELIMITER ';' CSV HEADER;