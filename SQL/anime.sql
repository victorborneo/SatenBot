CREATE TABLE IF NOT EXISTS user(
    id TEXT,
    username TEXT,
    bonuses INT DEFAULT 0,
    daily INT DEFAULT 1,
    mdaily INT DEFAULT 1,
    next_vote TEXT,

    CONSTRAINT pk_id PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS guild(
    id TEXT,

    CONSTRAINT pk_id PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS anime(
    id TEXT,
    type TEXT,
    premiere TEXT,
    image TEXT UNIQUE,
    broadcast TEXT,
    score REAL,
    episodes INTEGER,
    airing TEXT NOT NULL,
    name TEXT NOT NULL,
    rank INTEGER NOT NULL,
    alt_name TEXT,
    value INT,

    CONSTRAINT pk_id PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS genre(
    id TEXT,
    name TEXT UNIQUE,

    CONSTRAINT pk_id PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS studio(
    id TEXT,
    name TEXT UNIQUE,

    CONSTRAINT pk_id PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS wishes(
    user_id TEXT,
    guild_id TEXT,
    anime_id TEXT,

    CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    CONSTRAINT fk_anime_id FOREIGN KEY (anime_id) REFERENCES anime(id) ON DELETE CASCADE,
    CONSTRAINT fk_guild_id FOREIGN KEY (guild_id) REFERENCES guild(id) ON DELETE CASCADE,

    CONSTRAINT pk_user_anime_guild_id PRIMARY KEY (anime_id, user_id, guild_id)
);

CREATE TABLE IF NOT EXISTS user_guild_data(
    user_id TEXT,
    guild_id TEXT,
    rolls INT DEFAULT 1,
    balance INT DEFAULT 0,
    next_bonus TEXT,
    wl_limit INT DEFAULT 10,
    wl_boost REAL DEFAULT 1,

    CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    CONSTRAINT fk_guild_id FOREIGN KEY (guild_id) REFERENCES guild(id) ON DELETE CASCADE,

    CONSTRAINT pk_user_guild_id PRIMARY KEY (user_id, guild_id)
);

CREATE TABLE IF NOT EXISTS obtains(
    user_id TEXT,
    anime_id TEXT,
    guild_id TEXT,
    amount INT,

    CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    CONSTRAINT fk_anime_id FOREIGN KEY (anime_id) REFERENCES anime(id) ON DELETE CASCADE,
    CONSTRAINT fk_guild_id FOREIGN KEY (guild_id) REFERENCES guild(id) ON DELETE CASCADE,

    CONSTRAINT pk_user_anime_guild_id PRIMARY KEY (anime_id, user_id, guild_id)
);

CREATE TABLE IF NOT EXISTS notifies(
    user_id TEXT,
    anime_id TEXT,

    CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    CONSTRAINT fk_anime_id FOREIGN KEY (anime_id) REFERENCES anime(id) ON DELETE CASCADE,

    CONSTRAINT pk_user_anime_id PRIMARY KEY (anime_id, user_id)
);

CREATE TABLE IF NOT EXISTS produced(
    anime_id TEXT,
    studio_id TEXT,

    CONSTRAINT fk_anime_id FOREIGN KEY (anime_id) REFERENCES anime(id) ON DELETE CASCADE,
    CONSTRAINT fk_studio_id FOREIGN KEY (studio_id) REFERENCES studio(id) ON DELETE CASCADE,

    CONSTRAINT pk_anime_studio_id PRIMARY KEY (anime_id, studio_id)
);

CREATE TABLE IF NOT EXISTS has(
    anime_id TEXT,
    genre_id TEXT,

    CONSTRAINT fk_anime_id FOREIGN KEY (anime_id) REFERENCES anime(id) ON DELETE CASCADE,
    CONSTRAINT fk_genre_id FOREIGN KEY (genre_id) REFERENCES genre(id) ON DELETE CASCADE,

    CONSTRAINT pk_anime_genre_id PRIMARY KEY (anime_id, genre_id)
);
