const courses = [
  {
    title: "Scan the desk",
    body: "Hackfind pulls from Devpost, Devfolio, MLH, and HackerEarth so you stop refreshing five tabs.",
  },
  {
    title: "Clip your band",
    body: "Saved filters keep only the stack, mode, and domain that fit you. Noise never gets a clip.",
  },
  {
    title: "Don’t miss the stamp",
    body: "Deadline reminders hit at 7 days, 1 day, and day-of — before the band expires.",
  },
] as const;

export function HowItWorks() {
  return (
    <section className="border-t border-rail bg-field">
      <div className="mx-auto max-w-6xl px-6 py-20">
        <h2 className="font-display max-w-[18ch] text-3xl font-semibold tracking-tight text-balance sm:text-4xl">
          Three stations. Then you’re checked in.
        </h2>
        <p className="mt-4 max-w-[58ch] text-muted text-pretty">
          Same ritual as a hackathon desk — scan, clip, stamp — without the
          queue.
        </p>

        <ol className="mt-14 space-y-0">
          {courses.map((course, index) => (
            <li
              key={course.title}
              className="grid gap-4 border-t border-rail py-8 sm:grid-cols-[7rem_1fr] sm:gap-10"
            >
              <p className="font-mono text-sm tracking-[0.12em] text-deep uppercase">
                Course {String(index + 1).padStart(2, "0")}
              </p>
              <div>
                <h3 className="font-display text-xl font-semibold tracking-tight">
                  {course.title}
                </h3>
                <p className="mt-2 max-w-[62ch] text-muted text-pretty">
                  {course.body}
                </p>
              </div>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
