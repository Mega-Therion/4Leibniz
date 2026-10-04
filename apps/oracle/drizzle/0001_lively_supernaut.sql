CREATE TABLE `saved_insight_sync` (
	`id` int AUTO_INCREMENT NOT NULL,
	`userOpenId` varchar(64) NOT NULL,
	`payload` text NOT NULL,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `saved_insight_sync_id` PRIMARY KEY(`id`),
	CONSTRAINT `saved_insight_sync_userOpenId_unique` UNIQUE(`userOpenId`)
);
