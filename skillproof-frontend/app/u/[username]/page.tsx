interface Props {
  params: Promise<{ username: string }>;
}

export default async function PublicProfilePage({ params }: Props) {
  const { username } = await params;
  return (
    <div className="p-8">
      <h1 className="text-2xl font-semibold">
        Public Profile: @{username} — stub page
      </h1>
    </div>
  );
}
