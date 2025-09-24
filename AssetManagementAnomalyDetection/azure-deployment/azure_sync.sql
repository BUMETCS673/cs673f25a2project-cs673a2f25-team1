-- Generated SQL Server sync script from local SQLite data
SET NOCOUNT ON;
GO

IF OBJECT_ID('dbo.portfolios','U') IS NULL
		CREATE TABLE dbo.portfolios (
			id INT IDENTITY(1,1) PRIMARY KEY,
			name NVARCHAR(100) NOT NULL,
			manager NVARCHAR(100) NOT NULL,
			total_assets FLOAT NOT NULL,
			created_at DATETIME2 DEFAULT GETUTCDATE()
		);
GO

IF OBJECT_ID('dbo.assets','U') IS NULL
		CREATE TABLE dbo.assets (
			id INT IDENTITY(1,1) PRIMARY KEY,
			portfolio_id INT NOT NULL,
			symbol NVARCHAR(10) NOT NULL,
			name NVARCHAR(100) NOT NULL,
			quantity FLOAT NOT NULL,
			purchase_price FLOAT NOT NULL,
			current_price FLOAT NULL,
			purchase_date DATE NOT NULL,
			FOREIGN KEY (portfolio_id) REFERENCES dbo.portfolios(id)
		);
GO

IF OBJECT_ID('dbo.fees','U') IS NULL
		CREATE TABLE dbo.fees (
			id INT IDENTITY(1,1) PRIMARY KEY,
			portfolio_id INT NOT NULL,
			amount FLOAT NOT NULL,
			date DATE NOT NULL,
			fee_type NVARCHAR(50) NOT NULL,
			description NVARCHAR(MAX) NULL,
			FOREIGN KEY (portfolio_id) REFERENCES dbo.portfolios(id)
		);
GO

IF OBJECT_ID('dbo.anomalies','U') IS NULL
		CREATE TABLE dbo.anomalies (
			id INT IDENTITY(1,1) PRIMARY KEY,
			portfolio_id INT NOT NULL,
			fee_id INT NOT NULL,
			anomaly_score FLOAT NOT NULL,
			detected_at DATETIME2 DEFAULT GETUTCDATE(),
			reviewed BIT DEFAULT 0,
			FOREIGN KEY (portfolio_id) REFERENCES dbo.portfolios(id),
			FOREIGN KEY (fee_id) REFERENCES dbo.fees(id)
		);
GO

DELETE FROM dbo.anomalies;
GO
DELETE FROM dbo.fees;
GO
DELETE FROM dbo.assets;
GO
DELETE FROM dbo.portfolios;
GO

SET IDENTITY_INSERT dbo.portfolios ON;
INSERT INTO dbo.portfolios ([id], [name], [manager], [total_assets], [created_at]) VALUES (1, 'Tech Growth Fund', 'Alpha Investments', 50000000.0, '2025-09-23 06:00:35.887076');
INSERT INTO dbo.portfolios ([id], [name], [manager], [total_assets], [created_at]) VALUES (2, 'Balanced Portfolio', 'Beta Capital', 75000000.0, '2025-09-23 06:00:35.887084');
INSERT INTO dbo.portfolios ([id], [name], [manager], [total_assets], [created_at]) VALUES (3, 'Conservative Fund', 'Gamma Advisors', 30000000.0, '2025-09-23 06:00:35.887088');
INSERT INTO dbo.portfolios ([id], [name], [manager], [total_assets], [created_at]) VALUES (4, 'Emerging Markets', 'Delta Management', 40000000.0, '2025-09-23 06:00:35.887091');
SET IDENTITY_INSERT dbo.portfolios OFF;
GO

SET IDENTITY_INSERT dbo.assets ON;
INSERT INTO dbo.assets ([id], [portfolio_id], [symbol], [name], [quantity], [purchase_price], [current_price], [purchase_date]) VALUES (1, 1, 'AST11', 'Asset 1 - Tech Growth Fund', 7367.212715688306, 87.9491810234167, 328.53778245965117, '2025-06-10');
INSERT INTO dbo.assets ([id], [portfolio_id], [symbol], [name], [quantity], [purchase_price], [current_price], [purchase_date]) VALUES (2, 1, 'AST21', 'Asset 2 - Tech Growth Fund', 8590.03355677319, 443.8097996975375, 32.774267251263105, '2025-01-01');
INSERT INTO dbo.assets ([id], [portfolio_id], [symbol], [name], [quantity], [purchase_price], [current_price], [purchase_date]) VALUES (3, 1, 'AST31', 'Asset 3 - Tech Growth Fund', 7159.771292218665, 161.6405969042674, 341.01509108491143, '2024-10-23');
INSERT INTO dbo.assets ([id], [portfolio_id], [symbol], [name], [quantity], [purchase_price], [current_price], [purchase_date]) VALUES (4, 1, 'AST41', 'Asset 4 - Tech Growth Fund', 4908.463047043645, 13.798201323208875, 499.3490479085275, '2024-12-05');
INSERT INTO dbo.assets ([id], [portfolio_id], [symbol], [name], [quantity], [purchase_price], [current_price], [purchase_date]) VALUES (5, 1, 'AST51', 'Asset 5 - Tech Growth Fund', 9406.667839016825, 281.1314930634743, 318.49983281141596, '2025-06-05');
INSERT INTO dbo.assets ([id], [portfolio_id], [symbol], [name], [quantity], [purchase_price], [current_price], [purchase_date]) VALUES (6, 2, 'AST12', 'Asset 1 - Balanced Portfolio', 4823.207893650055, 15.236405273796743, 254.2988746617445, '2025-06-29');
INSERT INTO dbo.assets ([id], [portfolio_id], [symbol], [name], [quantity], [purchase_price], [current_price], [purchase_date]) VALUES (7, 2, 'AST22', 'Asset 2 - Balanced Portfolio', 1217.4144145194814, 192.7423399518348, 360.2259884645213, '2025-04-26');
INSERT INTO dbo.assets ([id], [portfolio_id], [symbol], [name], [quantity], [purchase_price], [current_price], [purchase_date]) VALUES (8, 2, 'AST32', 'Asset 3 - Balanced Portfolio', 8694.278601007763, 187.8205000926755, 409.6857144366384, '2024-12-30');
INSERT INTO dbo.assets ([id], [portfolio_id], [symbol], [name], [quantity], [purchase_price], [current_price], [purchase_date]) VALUES (9, 2, 'AST42', 'Asset 4 - Balanced Portfolio', 1069.4683337394194, 412.72432927764004, 312.1661134990022, '2025-03-26');
INSERT INTO dbo.assets ([id], [portfolio_id], [symbol], [name], [quantity], [purchase_price], [current_price], [purchase_date]) VALUES (10, 2, 'AST52', 'Asset 5 - Balanced Portfolio', 1712.2226151387708, 80.48528688411295, 495.178758280524, '2024-11-29');
INSERT INTO dbo.assets ([id], [portfolio_id], [symbol], [name], [quantity], [purchase_price], [current_price], [purchase_date]) VALUES (11, 3, 'AST13', 'Asset 1 - Conservative Fund', 5129.055481146012, 197.98632645536517, 58.13859107320119, '2025-05-22');
INSERT INTO dbo.assets ([id], [portfolio_id], [symbol], [name], [quantity], [purchase_price], [current_price], [purchase_date]) VALUES (12, 3, 'AST23', 'Asset 2 - Conservative Fund', 6464.144007933591, 103.86411475427197, 36.02237420059372, '2025-05-18');
INSERT INTO dbo.assets ([id], [portfolio_id], [symbol], [name], [quantity], [purchase_price], [current_price], [purchase_date]) VALUES (13, 3, 'AST33', 'Asset 3 - Conservative Fund', 4856.786500013566, 258.7826616004233, 89.65932446036317, '2025-03-12');
INSERT INTO dbo.assets ([id], [portfolio_id], [symbol], [name], [quantity], [purchase_price], [current_price], [purchase_date]) VALUES (14, 3, 'AST43', 'Asset 4 - Conservative Fund', 3435.836026924219, 241.99832097856114, 320.719715231581, '2024-12-22');
INSERT INTO dbo.assets ([id], [portfolio_id], [symbol], [name], [quantity], [purchase_price], [current_price], [purchase_date]) VALUES (15, 3, 'AST53', 'Asset 5 - Conservative Fund', 7488.136429064572, 329.9846663065514, 74.96006792451816, '2025-03-30');
INSERT INTO dbo.assets ([id], [portfolio_id], [symbol], [name], [quantity], [purchase_price], [current_price], [purchase_date]) VALUES (16, 4, 'AST14', 'Asset 1 - Emerging Markets', 6241.007931653269, 329.0498162275535, 261.9497178712352, '2025-02-23');
INSERT INTO dbo.assets ([id], [portfolio_id], [symbol], [name], [quantity], [purchase_price], [current_price], [purchase_date]) VALUES (17, 4, 'AST24', 'Asset 2 - Emerging Markets', 4168.72451817101, 137.92806740045853, 98.90102710086913, '2024-10-06');
INSERT INTO dbo.assets ([id], [portfolio_id], [symbol], [name], [quantity], [purchase_price], [current_price], [purchase_date]) VALUES (18, 4, 'AST34', 'Asset 3 - Emerging Markets', 5313.707881706643, 208.91120320089476, 72.69786755198248, '2025-05-31');
INSERT INTO dbo.assets ([id], [portfolio_id], [symbol], [name], [quantity], [purchase_price], [current_price], [purchase_date]) VALUES (19, 4, 'AST44', 'Asset 4 - Emerging Markets', 3491.033264009045, 322.0434979734831, 452.85588296805685, '2025-03-17');
INSERT INTO dbo.assets ([id], [portfolio_id], [symbol], [name], [quantity], [purchase_price], [current_price], [purchase_date]) VALUES (20, 4, 'AST54', 'Asset 5 - Emerging Markets', 578.2377165478399, 378.64539977448214, 70.36205548666248, '2025-02-11');
SET IDENTITY_INSERT dbo.assets OFF;
GO

SET IDENTITY_INSERT dbo.fees ON;
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (1, 1, 1.3471287979683098, '2025-09-23', 'management', 'Monthly management fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (2, 1, 1.0481981051319187, '2025-08-24', 'administrative', 'Monthly administrative fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (3, 1, 1.1041617039795544, '2025-07-25', 'administrative', 'Monthly performance fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (4, 1, 1.4822097627025277, '2025-06-25', 'management', 'Monthly management fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (5, 1, 1.0456607610586939, '2025-05-26', 'administrative', 'Monthly management fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (6, 1, 1.173730543430193, '2025-04-26', 'performance', 'Monthly performance fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (7, 1, 1.4949267842130374, '2025-03-27', 'administrative', 'Monthly administrative fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (8, 1, 1.282238189291627, '2025-02-25', 'administrative', 'Monthly management fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (9, 1, 1.3203521783677878, '2025-01-26', 'administrative', 'Monthly administrative fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (10, 1, 1.3044387719018737, '2024-12-27', 'management', 'Monthly administrative fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (11, 1, 1.470834966283039, '2024-11-27', 'administrative', 'Monthly management fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (12, 1, 1.431220543662442, '2024-10-28', 'performance', 'Monthly performance fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (13, 2, 0.8633671630166462, '2025-09-23', 'administrative', 'Monthly performance fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (14, 2, 0.9833102982742236, '2025-08-24', 'administrative', 'Monthly administrative fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (15, 2, 0.958764621507286, '2025-07-25', 'performance', 'Monthly administrative fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (16, 2, 0.9198085759314387, '2025-06-25', 'administrative', 'Monthly management fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (17, 2, 0.8873360300431358, '2025-05-26', 'management', 'Monthly management fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (18, 2, 0.8242948192352348, '2025-04-26', 'administrative', 'Monthly management fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (19, 2, 0.6949446694495905, '2025-03-27', 'performance', 'Monthly administrative fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (20, 2, 2.83771982813372, '2025-02-25', 'management', 'Monthly management fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (21, 2, 2.226852927247929, '2025-01-26', 'administrative', 'Monthly management fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (22, 2, 3.3239769424663006, '2024-12-27', 'performance', 'Monthly management fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (23, 2, 3.2495452827922775, '2024-11-27', 'management', 'Monthly performance fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (24, 2, 2.743402699203003, '2024-10-28', 'management', 'Monthly management fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (25, 3, 1.1440390247941903, '2025-09-23', 'administrative', 'Monthly performance fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (26, 3, 0.8437730858387981, '2025-08-24', 'management', 'Monthly administrative fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (27, 3, 0.8301934156350513, '2025-07-25', 'performance', 'Monthly performance fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (28, 3, 1.0862594065140159, '2025-06-25', 'performance', 'Monthly administrative fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (29, 3, 1.0468017004532177, '2025-05-26', 'management', 'Monthly administrative fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (30, 3, 1.0847869192505173, '2025-04-26', 'performance', 'Monthly administrative fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (31, 3, 0.8435432999189852, '2025-03-27', 'performance', 'Monthly performance fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (32, 3, 1.1626819292365274, '2025-02-25', 'administrative', 'Monthly performance fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (33, 3, 1.0488794123285272, '2025-01-26', 'management', 'Monthly performance fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (34, 3, 0.9199193775726738, '2024-12-27', 'management', 'Monthly performance fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (35, 3, 0.9642059865583451, '2024-11-27', 'administrative', 'Monthly management fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (36, 3, 0.9902816332233174, '2024-10-28', 'administrative', 'Monthly administrative fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (37, 4, 0.7989466871336497, '2025-09-23', 'management', 'Monthly administrative fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (38, 4, 0.8699480593035792, '2025-08-24', 'management', 'Monthly management fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (39, 4, 0.9506305296408889, '2025-07-25', 'management', 'Monthly performance fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (40, 4, 0.8978971467690006, '2025-06-25', 'management', 'Monthly administrative fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (41, 4, 0.900263591923902, '2025-05-26', 'performance', 'Monthly management fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (42, 4, 0.8554391220799299, '2025-04-26', 'management', 'Monthly administrative fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (43, 4, 0.8119393381484936, '2025-03-27', 'performance', 'Monthly performance fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (44, 4, 3.437008239073323, '2025-02-25', 'performance', 'Monthly performance fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (45, 4, 3.480249904136316, '2025-01-26', 'administrative', 'Monthly administrative fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (46, 4, 3.425724372927927, '2024-12-27', 'administrative', 'Monthly administrative fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (47, 4, 2.5135870357687926, '2024-11-27', 'administrative', 'Monthly management fee');
INSERT INTO dbo.fees ([id], [portfolio_id], [amount], [date], [fee_type], [description]) VALUES (48, 4, 3.0337688394777085, '2024-10-28', 'performance', 'Monthly administrative fee');
SET IDENTITY_INSERT dbo.fees OFF;
GO

