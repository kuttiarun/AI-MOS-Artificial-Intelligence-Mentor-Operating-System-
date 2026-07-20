# Servlets & JSP — HTTP Lifecycle, Request/Response & Filter Chain

## What You'll Master
- The Servlet lifecycle and how Java EE handles HTTP
- Reading request parameters, headers, and body
- JSP — server-side HTML generation
- Filters and Listeners — cross-cutting concerns

---

## What Is a Servlet?

A **Servlet** is a Java class that handles HTTP requests on a server (Tomcat, Jetty). It's the foundation of all Java web frameworks including Spring MVC.

```
Browser → HTTP Request → Tomcat → Servlet → Business Logic → HTTP Response → Browser
```

---

## Servlet Lifecycle

```java
@WebServlet("/hello")
public class HelloServlet extends HttpServlet {

    // Called ONCE when servlet is loaded
    @Override
    public void init(ServletConfig config) throws ServletException {
        System.out.println("Servlet initialized");
    }

    // Called for EVERY GET request
    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws IOException {
        String name = req.getParameter("name");      // query param
        String auth = req.getHeader("Authorization"); // header

        resp.setContentType("text/html");
        resp.setStatus(HttpServletResponse.SC_OK);    // 200

        PrintWriter out = resp.getWriter();
        out.println("<h1>Hello, " + name + "!</h1>");
    }

    // Called for EVERY POST request
    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp)
            throws IOException {
        String body = req.getReader().lines()
                         .collect(Collectors.joining());
        // process JSON body...
        resp.setStatus(HttpServletResponse.SC_CREATED); // 201
    }

    // Called ONCE when servlet is destroyed
    @Override
    public void destroy() {
        System.out.println("Servlet destroyed");
    }
}
```

**Lifecycle**: `init()` → `service()` (calls doGet/doPost) → `destroy()`

---

## Session Management

```java
// HttpSession — stored server-side
HttpSession session = req.getSession(); // creates if not exists
session.setAttribute("user", currentUser);
session.setMaxInactiveInterval(1800);  // 30 min timeout

// Read session
User user = (User) session.getAttribute("user");

// Invalidate on logout
session.invalidate();

// Cookie
Cookie cookie = new Cookie("theme", "dark");
cookie.setMaxAge(7 * 24 * 3600); // 7 days
cookie.setHttpOnly(true);  // not accessible via JavaScript
cookie.setSecure(true);    // HTTPS only
resp.addCookie(cookie);
```

---

## Filters — Cross-Cutting Concerns

```java
@WebFilter("/*") // intercepts ALL requests
public class AuthFilter implements Filter {

    @Override
    public void doFilter(ServletRequest req, ServletResponse resp, FilterChain chain)
            throws IOException, ServletException {

        HttpServletRequest httpReq = (HttpServletRequest) req;
        String token = httpReq.getHeader("Authorization");

        if (token == null || !isValid(token)) {
            ((HttpServletResponse) resp).setStatus(401);
            resp.getWriter().write("Unauthorized");
            return; // stop chain
        }

        chain.doFilter(req, resp); // proceed to next filter or servlet
    }
}
```

**Filter Order**: Request → Filter1 → Filter2 → Servlet → Filter2 → Filter1 → Response

---

## JSP (JavaServer Pages) Basics

JSP = HTML + Java embedded in `<% %>` tags. Compiled into a Servlet by Tomcat.

```jsp
<%@ page language="java" contentType="text/html" %>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c" %>
<!DOCTYPE html>
<html>
<body>
  <h1>Welcome, ${user.name}!</h1>   <!-- EL Expression -->

  <c:forEach items="${products}" var="p">   <!-- JSTL tag -->
    <p>${p.name} - ₹${p.price}</p>
  </c:forEach>

  <%  // Scriptlet — avoid in modern code
      String msg = "Legacy approach";
      out.println(msg);
  %>
</body>
</html>
```

**Best practice**: Use JSTL + EL expressions, NOT scriptlets (`<% %>`).

---

## Servlet vs Spring MVC

| Feature | Servlet | Spring MVC |
|---|---|---|
| Request routing | `@WebServlet("/path")` | `@GetMapping("/path")` |
| Dependency injection | Manual | Automatic (`@Autowired`) |
| JSON binding | Manual Jackson | Automatic (`@RequestBody`) |
| Filter | `Filter` interface | `HandlerInterceptor` |
| Config | `web.xml` or annotations | `application.yml` |

> In production, you'll use Spring MVC. But understanding Servlets explains **why** Spring works the way it does.

---

## Revision Checkpoint

> Explain the difference between `doGet()` and `doPost()` and when you'd use each. When is it appropriate to store data in a session vs a cookie?
