import os
import asyncio

import discord
from discord import app_commands
from dotenv import load_dotenv

from main import run


# ==========================
# .env読み込み
# ==========================

load_dotenv()

TOKEN = os.getenv(
    "DISCORD_TOKEN"
)


# ==========================
# Discord Bot本体
# ==========================

class MyBot(discord.Client):

    def __init__(self):

        super().__init__(
            intents=discord.Intents.default()
        )

        self.tree = app_commands.CommandTree(
            self
        )


client = MyBot()


# ==========================
# Bot起動時
# ==========================

@client.event
async def on_ready():

    print(
        f"{client.user} としてログインしました"
    )

    synced = await client.tree.sync()

    print(
        f"{len(synced)}個のコマンドを同期しました"
    )


# ==========================
# /test
# ==========================

@client.tree.command(
    name="test",
    description="Botのテストをします"
)
async def test(
    interaction: discord.Interaction
):

    await interaction.response.send_message(
        "Botは正常に動いています！"
    )


# ==========================
# /pokemon
# ==========================

@client.tree.command(
    name="pokemon",
    description="Pokemon Championsの大会を検索します"
)
async def pokemon(
    interaction: discord.Interaction
):

    # まずDiscordに処理開始を通知
    await interaction.response.send_message(
        "🔍 Pokemon Championsの大会を検索しています..."
    )

    try:

        # スクレイピング処理を別スレッドで実行
        results, count = await asyncio.to_thread(
            run
        )


        # ==========================
        # Embed作成
        # ==========================

        embeds = []


        # 最初のEmbed
        embed = discord.Embed(
            title="🎮 Pokemon Champions 大会検索結果",
            description="検索が完了しました！"
        )


        # Embedの現在の文字数を管理
        current_size = (
            len(embed.title or "")
            + len(embed.description or "")
        )


        # ==========================
        # カテゴリーごとに処理
        # ==========================

        for category, events in results.items():

            # 大会がないカテゴリーは飛ばす
            if not events:
                continue


            text = ""


            # 大会を1つずつ処理
            for title, url in events:

                event_text = (
                    f"**{title}**\n"
                    f"{url}\n\n"
                )


                # Fieldが1000文字を超えそうなら
                if len(text) + len(event_text) > 1000:


                    # Embed全体が5500文字を超えそうなら
                    if (
                        current_size
                        + len(category)
                        + len(text)
                        > 5500
                    ):

                        # 現在のEmbedを保存
                        embeds.append(
                            embed
                        )


                        # 新しいEmbedを作成
                        embed = discord.Embed(
                            title="🎮 Pokemon Champions 大会検索結果（続き）"
                        )


                        current_size = len(
                            embed.title or ""
                        )


                    # Fieldを追加
                    embed.add_field(
                        name=category,
                        value=text,
                        inline=False
                    )


                    # 現在の文字数を更新
                    current_size += (
                        len(category)
                        + len(text)
                    )


                    # 次のField用にリセット
                    text = ""


                # 大会情報を追加
                text += event_text


            # ==========================
            # カテゴリーの残りを追加
            # ==========================

            if text:


                # Embed全体が大きくなりすぎる場合
                if (
                    current_size
                    + len(category)
                    + len(text)
                    > 5500
                ):


                    # 現在のEmbedを保存
                    embeds.append(
                        embed
                    )


                    # 新しいEmbed
                    embed = discord.Embed(
                        title="🎮 Pokemon Champions 大会検索結果（続き）"
                    )


                    current_size = len(
                        embed.title or ""
                    )


                # Field追加
                embed.add_field(
                    name=category,
                    value=text,
                    inline=False
                )


                # 文字数更新
                current_size += (
                    len(category)
                    + len(text)
                )


        # ==========================
        # 最後のEmbedを保存
        # ==========================

        if embed.fields:

            embeds.append(
                embed
            )


        # ==========================
        # 最後に合計大会数を表示
        # ==========================

        if embeds:

            embeds[-1].set_footer(
                text=f"合計大会数: {count}"
            )


        # ==========================
        # EmbedをDiscordへ送信
        # ==========================

        for result_embed in embeds:

            await interaction.followup.send(
                embed=result_embed
            )


            # 連続送信しすぎないよう少し待つ
            await asyncio.sleep(
                0.3
            )


        # 大会が見つからなかった場合
        if not embeds:

            await interaction.followup.send(
                "大会が見つかりませんでした。"
            )


    except Exception as e:

        # PowerShellにもエラー表示
        print(e)


        # Discordにもエラー表示
        await interaction.followup.send(
            f"❌ エラーが発生しました。\n"
            f"```{e}```"
        )


# ==========================
# Bot起動
# ==========================

client.run(
    TOKEN
)