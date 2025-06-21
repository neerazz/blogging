# From 50 Million Events to a Single Answer: Building a RAG Pipeline in Spring Boot

I still remember the Slack message from a junior dev on a Tuesday morning. It was a single, dreaded question about a critical Log4j vulnerability. I knew the answer was buried somewhere in our beautifully complex vulnerability management system—my magnum opus of filtering—but I also knew he'd never find it.

A few years ago, I led the team that built that system. It was a beast, processing over 50 million security checks a month with a slick pipeline using Kafka and Google BigQuery. And yet, there I was, typing out the answer for him manually.

We hadn't built a solution; we'd built a beautiful, data-rich island that only a few experts knew how to navigate. It wasn't a data problem; it was an access problem.

## The Sound of Crickets

Our first attempt to fix this was... more dashboards. It was a humbling experience. I'd championed this data-first approach, and the sound of crickets in the user adoption channel was deafening.

I used to think that if you just presented enough data, the insights would be obvious. It was a painful lesson, but I was wrong. We needed a system that could understand a developer's intent, not just their keywords.

Then the AI hype train pulled into the station. I spent a weekend trying to hook up a generic LLM API to our database. The results were terrifying. It would confidently invent vulnerabilities, suggest wildly incorrect fixes, and completely hallucinate policy details. It was a dangerous toy, not a professional tool.

## The Aha Moment: It's a Librarian, Not an Oracle

After that failed weekend, I was ready to give up. Then, scrolling through a research paper, I saw a diagram for Retrieval-Augmented Generation (RAG) and it all clicked. As I discovered in Spring AI's documentation, "Retrieval Augmented Generation (RAG) has emerged to address the challenge of incorporating relevant data into prompts for accurate AI model responses."

This boils down to one key idea: The LLM isn't the brain; it's the voice. We didn't need a know-it-all oracle. We needed a world-class librarian who could fetch the right book, open it to the right page, highlight the exact sentence we needed, and hand it to the LLM. The LLM's only job was to read that sentence out loud.

Suddenly, all our hard-won skills in building data pipelines with Java were the perfect foundation for enterprise AI. As Josh Long recently explained, "90% of what people talk about when they talk about AI engineering is just integration with models" - and what better place for integrations than Spring?

## Let's Demystify This: Building a RAG Bot in Java

Let's build a simplified version of this. Our goal: a Q&A API that uses our internal documents as its source of truth.

First things first, you'll need a Spring Boot 3.x project. The magic begins by adding the Spring AI starter to your pom.xml.

```xml
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-openai-spring-boot-starter</artifactId>
</dependency>

```

(I've put a link to a full, working version of this code on GitHub at the end!)

### Step 1: The 'Retrieval' - Teaching it What to Read

Next, we need to load our documents (e.g., Markdown security policies) into a Vector Store on startup. This process reads, splits, and converts the documents into numerical embeddings the AI can search.

As Dan Vega suggests in his guide, "Create a service to handle document processing and storage":

```java
// In your Spring Boot Application or a @Configuration class
@Bean
ApplicationRunner runner(VectorStore vectorStore, ResourceLoader resourceLoader) {
    return args -> {
        // Point to a folder with your .md files
        Resource[] resources = resourceLoader.getResources("classpath:docs/*.md");
        var textSplitter = new TokenTextSplitter();

        // This loop is crucial! It ensures ALL documents are processed.
        for (Resource resource : resources) {
            var textReader = new TextReader(resource);
            textReader.setCharset(StandardCharsets.UTF_8);
            vectorStore.add(textSplitter.apply(textReader.get()));
        }

        System.out.println("Documents loaded into Vector Store.");
    };
}

```

**Common Mistake**: Forgetting to loop through your resources. I made this mistake at first, and my bot could only answer questions about the first document it found!

For production applications, Piotr Minkowski recommends, "Use chunks that are too large (loses focus) or too small (loses context)". The sweet spot is usually between 500-1000 tokens per chunk.

### Step 2: The 'Augment & Generate' - The Q&A Endpoint

Now for the fun part. We create a REST controller that takes a question, searches the VectorStore for relevant text, and "augments" a prompt with that context before sending it to the LLM.

```java
// In your @RestController
@Autowired
private ChatClient chatClient;
@Autowired
private VectorStore vectorStore;

@GetMapping("/ask")
public String ask(@RequestParam String question) {
    // 1. Search the vector store for documents relevant to the question
    List<Document> relevantDocs = vectorStore.similaritySearch(question);
    String context = relevantDocs.stream()
            .map(Document::getContent)
            .collect(Collectors.joining("\n"));

    // 2. Create a prompt template that injects the context
    String promptText = """
            You are a helpful security assistant. Answer the following question based ONLY on the provided context.
            If the answer is not in the context, say 'I don't have enough information to answer that.'

            CONTEXT:
            {context}

            QUESTION:
            {question}
            """;

    // 3. Send the complete prompt to the LLM
    PromptTemplate promptTemplate = new PromptTemplate(promptText);
    Prompt prompt = promptTemplate.create(Map.of("context", context, "question", question));

    return chatClient.call(prompt).getResult().getOutput().getContent();
}

```

**Pro-Tip**: In a real app, never hardcode a prompt like this. Load it from a .st template file or a config property. It makes your prompts much easier to manage and version control.

## Choosing the Right Vector Database

When it comes to vector databases, you have many excellent options. Spring AI supports various vector databases including:

- **PostgreSQL with pgvector**: Great for teams already using PostgreSQL. As documented in recent guides, "pgvector provides a good balance between search speed and accuracy".
- **Elasticsearch**: Perfect for enterprise setups, especially if you're already using Elastic Stack.
- **ChromaDB**: Ideal for local development and prototyping.
- **Pinecone**: A cloud-native solution that scales effortlessly.

For our vulnerability management system, we chose PostgreSQL with pgvector because we already had PostgreSQL expertise on the team. The setup was surprisingly straightforward!

## Advanced RAG Techniques

As your system grows, you'll want to explore advanced features. Marcus Hellberg from Vaadin explains, "Spring AI recently introduced the RetrievalAugmentationAdvisor, an experimental feature that provides a modular approach to building RAG pipelines".

This allows you to:

- Implement query rewriting for better results
- Add semantic caching to reduce API costs
- Use hybrid search combining keyword and vector similarity
- Implement dynamic chunk sizing based on content type

## Your Skills Are More Relevant Than Ever

We shifted from building complex UIs that forced users to search to simple APIs that let them ask. This was the first step toward true, developer-first security.

Bridging the gap between different technologies taught me that no skill is ever wasted. As Craig Walls puts it in "Spring AI in Action", "You need some experience with Spring and Spring Boot. No Generative AI skills required." Trust me, if a guy who started his career maintaining COBOL batch jobs can make this leap into AI, you absolutely can. You don't need to be an AI researcher; you just need to be a pragmatic problem-solver.

So, here's my challenge: don't just read about it, try it. You can find the complete, working code for this post on [my GitHub](https://github.com/neerazz/SpringBootRAGPipeline).

Clone it, run it, and start with your own project's READMEs. What's the first document set you would want to "chat" with?

## Further Learning

Ready to dive deeper? Here are some carefully selected resources to accelerate your RAG journey:

### 📚 Essential Guides

- [**Spring AI Reference Documentation**](https://docs.spring.io/spring-ai/reference/) - The official comprehensive guide (1-2 hours)
- [**Building RAG Applications with Spring AI and Elasticsearch**](https://www.elastic.co/search-labs/blog/spring-ai-elasticsearch-rag) - Complete tutorial with code examples (45 minutes)
- [**Spring AI in Action**](https://www.manning.com/books/spring-ai-in-action) by Craig Walls - The definitive book on Spring AI (full book)

### 🎥 Video Tutorials

- [**Build Smarter Spring Boot Applications with Spring AI**](https://www.freecodecamp.org/news/build-smarter-spring-boot-applications-with-spring-ai/) - 5-hour comprehensive course on freeCodeCamp (Beginner-friendly)
- [**Spring Tips: Vector Databases**](https://spring.io/blog/2024/05/07/spring-tips-vector-databases-with-spring-ai/) by Josh Long - Deep dive into vector stores (30 minutes)

### 🛠️ Hands-On Projects

- [**GitHub: Spring AI Examples**](https://github.com/spring-projects/spring-ai/tree/main/spring-ai-docs/src/main/antora/modules/ROOT/examples) - Official example projects (2-4 hours per example)
- [**RAG Pipeline Using Spring AI Implementation**](https://github.com/Talentica/RAG-SpringAI.git) - Complete working example (1 hour)

### 👥 Follow the Experts

- **Josh Long** ([@starbuxman](https://twitter.com/starbuxman)) - Spring Developer Advocate, regular Spring AI content
- **Craig Walls** - Author of Spring AI in Action
- **Dan Vega** ([@therealdanvega](https://twitter.com/therealdanvega)) - Excellent Spring AI tutorials
- **Piotr Minkowski** - Regular technical deep-dives on Spring AI implementations

### 🌟 Community Resources

- [**Awesome Spring AI**](https://github.com/spring-ai-community/awesome-spring-ai) - Curated list of resources, constantly updated
- [**Spring AI Discord**](https://discord.gg/spring) - Active community for real-time help
- [**Spring I/O 2025 - Modular RAG Architectures**](https://2025.springio.net/sessions/modular-rag-architectures-with-java-and-spring-ai/) - Upcoming conference talk

Remember, the best way to learn is by doing. Start with a simple RAG implementation, then gradually add features like query rewriting, hybrid search, and advanced advisors. The Spring AI community is here to help you succeed!

---

*What's your first RAG project going to be? Share your ideas below!*

---

## Join the Conversation

Have you implemented RAG in your organization? What challenges did you face? Share your experiences in the comments below or reach out on social media using #SpringAI #RAGPipeline #JavaAI.

The Spring AI community is incredibly active. Join us on:

- The [Spring AI GitHub repository](https://github.com/spring-projects/spring-ai) for issues and contributions
- The [Awesome Spring AI](https://github.com/spring-ai-community/awesome-spring-ai) collection for curated resources
- Spring community forums and Discord channels