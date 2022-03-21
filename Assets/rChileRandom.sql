-- phpMyAdmin SQL Dump
-- version 5.1.0
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 20-03-2022 a las 20:45:09
-- Versión del servidor: 8.0.28-0ubuntu0.20.04.3
-- Versión de PHP: 7.4.3

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `rChileRandom`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `chile_users`
--

CREATE TABLE `chile_users` (
  `user_id` int NOT NULL,
  `user_username` varchar(32) COLLATE utf8_spanish_ci NOT NULL,
  `user_first_comment` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `random_comments`
--

CREATE TABLE `random_comments` (
  `comment_id` int NOT NULL,
  `comment_reddit_id` varchar(16) COLLATE utf8_spanish_ci NOT NULL,
  `comment_level` int NOT NULL DEFAULT '0',
  `comment_user_id` int NOT NULL,
  `comment_random_id` int NOT NULL,
  `comment_UTC` timestamp NOT NULL,
  `comment_number` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `random_posts`
--

CREATE TABLE `random_posts` (
  `post_id` int NOT NULL,
  `post_reddit_id` varchar(16) COLLATE utf8_spanish_ci NOT NULL,
  `post_week` int NOT NULL,
  `post_year` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8_spanish_ci;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `chile_users`
--
ALTER TABLE `chile_users`
  ADD PRIMARY KEY (`user_id`);

--
-- Indices de la tabla `random_comments`
--
ALTER TABLE `random_comments`
  ADD PRIMARY KEY (`comment_id`),
  ADD KEY `comment-user` (`comment_user_id`),
  ADD KEY `comment-random` (`comment_random_id`);

--
-- Indices de la tabla `random_posts`
--
ALTER TABLE `random_posts`
  ADD PRIMARY KEY (`post_id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `chile_users`
--
ALTER TABLE `chile_users`
  MODIFY `user_id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `random_comments`
--
ALTER TABLE `random_comments`
  MODIFY `comment_id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `random_posts`
--
ALTER TABLE `random_posts`
  MODIFY `post_id` int NOT NULL AUTO_INCREMENT;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `random_comments`
--
ALTER TABLE `random_comments`
  ADD CONSTRAINT `comment-random` FOREIGN KEY (`comment_random_id`) REFERENCES `random_posts` (`post_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `comment-user` FOREIGN KEY (`comment_user_id`) REFERENCES `chile_users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
