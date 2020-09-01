This directory has a snapshot of the MySQL database to this application, statistics-api. It's only used for testing during automatic deployment pipeline.

The enrollment counts and teacher counts of each school in this database, are not real. In order to falsify the data before saving it here, the following query was ran

UPDATE `county`
SET number_of_teachers=number_of_teachers + (SELECT FLOOR(RAND()*50) + 50);
UPDATE `school`
SET number_of_teachers=number_of_teachers + (SELECT FLOOR(RAND()*50) + 50);
UPDATE `group`
SET `group`.members_count=`group`.members_count + (SELECT FLOOR(RAND()*50));