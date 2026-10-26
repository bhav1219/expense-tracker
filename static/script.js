
// ADD EXPENSE

const expenseButton = document.getElementById("expenseButton");

expenseButton.addEventListener("click", async function () {
    const name = document.getElementById("expenseName").value.trim();
    const amount = document.getElementById("expenseAmount").value;
    const category = document.getElementById("expenseCategory").value;
    const date = document.getElementById("expenseDate").value;

    if (!name || !amount || !category || !date) {
        alert("Please fill all the fields");
        return;
    }

    if (Number(amount) <= 0) {
        alert("Amount must be greater than 0");
        return;
    }

    expenseButton.disabled = true;

    try {
        const response = await fetch("/add_expense", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                name: name,
                amount: amount,
                category: category,
                date: date
            })
        });

        if (response.ok) {
            alert("Expense added successfully!");
            location.reload();
        } else {
            const result = await response.json();
            alert(result.error || "Failed to add expense");
        }
    } catch (error) {
        alert("Could not connect to the server. Please try again.");
    } finally {
        expenseButton.disabled = false;
    }
});


// SET MONTHLY BUDGET

const budgetButton = document.getElementById("budgetButton");

budgetButton.addEventListener("click", async function () {
    const budgetInput = document.getElementById("budgetAmount");
    const amount = Number(budgetInput.value);

    if (budgetInput.value.trim() === "" || amount <= 0) {
        alert("Please enter a budget greater than 0");
        return;
    }

    budgetButton.disabled = true;

    try {
        const response = await fetch("/set_budget", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                amount: amount
            })
        });

        if (response.ok) {
            alert("Monthly budget updated successfully!");
            location.reload();
        } else {
            const result = await response.json();
            alert(result.error || "Failed to update budget");
        }
    } catch (error) {
        alert("Could not connect to the server. Please try again.");
    } finally {
        budgetButton.disabled = false;
    }
});


// FILTER EXPENSE HISTORY BY MONTH

const monthFilter = document.getElementById("monthFilter");

if (monthFilter) {
    monthFilter.addEventListener("change", function () {
        const selectedMonth = monthFilter.value;
        const monthCards = document.querySelectorAll(".month-card");
        const noMonthMessage = document.getElementById("noMonthMessage");

        let visibleCount = 0;

        monthCards.forEach(function (card) {
            const matches =
                selectedMonth === "all" ||
                card.dataset.month === selectedMonth;

            card.hidden = !matches;

            if (matches) {
                visibleCount++;
            }
        });

        if (noMonthMessage) {
            noMonthMessage.hidden = visibleCount !== 0;
        }
    });
}
