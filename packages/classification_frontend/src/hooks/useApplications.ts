import { useQuery } from "@tanstack/react-query";
import type { Application, ApplicationsResponse } from "@/lib/apiTypes";
import { fetchApplications } from "@/server/server";

export function useApplications(page = 1, pageSize = 10) {
  return useQuery<ApplicationsResponse>({
    queryKey: ["applications", page, pageSize],
    queryFn: () => fetchApplications(page, pageSize),
    enabled: true,
  });
}

// Helper function to find application in the applications array
export function findApplicationInList(
  applications: Application[],
  applicationId: string
): Application | undefined {
  return applications.find((app) => app.application_id === applicationId);
}
