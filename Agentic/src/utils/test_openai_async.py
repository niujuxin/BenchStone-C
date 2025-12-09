
if __name__ == "__main__":

    import asyncio
    import dotenv

    dotenv.load_dotenv()

    from openai import AsyncOpenAI
    from openai.types.responses import Response

    model, reasoning, verbosity = 'gpt-5-nano', 'minimal', 'low' 

    prompt = [
        'Write a C function that returns the factorial of a given integer n.',
        'Write a Python function that returns the factorial of a given integer n.'
        'Write a JavaScript function that returns the factorial of a given integer n.'
    ]

    async def main():
        client = AsyncOpenAI()
        tasks = []
        for p in prompt:
            tasks.append(
                client.responses.create(
                    model=model,
                    input=p,
                    reasoning = { "effort": reasoning },
                    text = { "verbosity": verbosity },
                )
            )

        responses: list[Response] = await asyncio.gather(*tasks)
        for resp in responses:
            content = resp.output_text
            print("Generated Code:\n", content)

    asyncio.run(main())

